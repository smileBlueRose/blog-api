from logging import getLogger
from typing import Any, cast

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.utils.serializer_helpers import ReturnList
from rest_framework.viewsets import ViewSet

from apps.posts.models import Post
from common.clear_cache import clear_cache
from common.get_required_field import require_field
from common.pagination import CustomPagination
from common.security import sanitize_html_input
from settings.conf import settings

from .models import Comment
from .serializers import CommentCreateSerializer, CommentRetrieveSerializer
from .service import CommentService

logger = getLogger(__name__)


class CommentViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "comment_id"
    paginator = CustomPagination()

    def _get_post(self, post_slug: str) -> Post:
        return Post.objects.get(slug=post_slug)

    def _clear_cache(self) -> None:
        clear_cache(prefix=settings.redis.prefix.comment_list)
        logger.debug("Cache cleared, prefix %r", settings.redis.prefix.comment_list)

    @method_decorator(cache_page(60, key_prefix=settings.redis.prefix.comment_list))
    def list(self, request: Request, post_slug: str) -> Response:
        logger.debug("Fetching comments, post_slug: %r", post_slug)

        comments = cast(
            list[Comment],
            self.paginator.paginate_queryset(
                queryset=Comment.objects.filter(post__slug=post_slug), request=request
            ),
        )

        if settings.log.debug_allowed:
            logger.debug("Found %s comments", len(comments))

        result = cast(ReturnList, CommentRetrieveSerializer(comments, many=True).data)
        return self.paginator.get_paginated_response(result)

    def create(self, request: Request, post_slug: str) -> Response:
        logger.info("Adding comment, post_slug: %r", post_slug)

        body: str = sanitize_html_input(
            require_field(cast(dict[str, Any], request.data), "body")
        )
        logger.debug("body: %r", body)

        serializer = CommentCreateSerializer(data={"body": body})
        serializer.is_valid(raise_exception=True)
        logger.debug("body validated")

        comment = serializer.save(post=self._get_post(post_slug), author=request.user)
        logger.info("Comment added")

        self._clear_cache()

        return Response(
            CommentRetrieveSerializer(comment).data, status=HTTP_201_CREATED
        )

    def delete(self, request: Request, post_slug: str, comment_id: int) -> Response:
        logger.info(
            "Deleting comment, user_id: %s, comment_id: %s", request.user.id, comment_id
        )
        logger.debug("post_slug: %r", post_slug)

        comment = Comment.objects.get(pk=comment_id)
        if post_slug != comment.post.slug:
            logger.warning("Comment doesn't belong to this post")
            return Response(
                {"error": "Comment doesnt' belong to this post"}, status=404
            )

        CommentService.check_permission_to_delete(user=request.user, comment=comment)
        logger.debug("Permission checks passed")

        comment.delete()
        logger.info("Comment deleted")

        self._clear_cache()

        return Response(status=HTTP_204_NO_CONTENT)

    def partial_update(self, request: Request, post_slug, comment_id: int) -> Response:
        logger.info(
            "Updating comment, user_id: %s, comment_id: %s", request.user.id, comment_id
        )
        logger.debug("post_slug: ", post_slug)

        comment = Comment.objects.get(pk=comment_id)
        if post_slug != comment.post.slug:
            logger.warning("Comment doesn't belong to this post")
            return Response(
                {"error": "Comment doesnt' belong to this post"}, status=404
            )

        CommentService.check_permission_to_update(user=request.user, comment=comment)
        logger.debug("Permission checks passed")

        body: str = sanitize_html_input(
            require_field(cast(dict[str, Any], request.data), "body")
        )
        logger.debug("body: %r", body)

        comment.body = body
        comment.save()
        logger.info("Comment updated")

        self._clear_cache()

        return Response(status=HTTP_204_NO_CONTENT)
