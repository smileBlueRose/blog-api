from logging import getLogger
from typing import Any, cast

from apps.posts.models import Post
from common.get_required_field import require_field
from common.security import sanitize_html_input
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ViewSet
from settings.conf import settings

from .models import Comment
from .serializers import CommentCreateSerializer, CommentRetrieveSerializer
from .service import CommentService

logger = getLogger(__name__)


class CommentViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "comment_id"

    def _get_post(self, post_slug: str) -> Post:
        return Post.objects.get(slug=post_slug)

    def list(self, request: Request, post_slug: str) -> Response:
        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))

        logger.debug(
            "Fetching comments, post_slug: %s, limit: %s, offset: %s",
            post_slug,
            limit,
            offset,
        )

        comments = Comment.objects.filter(post__slug=post_slug)[offset : offset + limit]

        if settings.log.debug_allowed:
            logger.debug("Found %s comments", len(comments))

        return Response(
            CommentRetrieveSerializer(comments, many=True).data, status=HTTP_200_OK
        )

    def create(self, request: Request, post_slug: str) -> Response:
        logger.info("Adding comment, post_slug: %r", post_slug)

        body: str = sanitize_html_input(
            require_field(cast(dict[str, Any], request.data), "body")
        )
        logger.debug("body: %s", body)

        serializer = CommentCreateSerializer(data={"body": body})
        serializer.is_valid(raise_exception=True)
        logger.debug("body validated")

        comment = serializer.save(post=self._get_post(post_slug), author=request.user)
        logger.info("Comment added")

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

        return Response(status=HTTP_204_NO_CONTENT)
