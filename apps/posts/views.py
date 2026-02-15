from logging import getLogger
from typing import Any, cast

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.viewsets import ViewSet

from common.clear_cache import clear_cache
from common.pagination import CustomPagination
from common.security import sanitize_data
from settings.base import settings

from .models import Post
from .serializers import PostCreateSerializer, PostRetrieveSerializer
from .service import PostService

logger = getLogger(__name__)


@method_decorator(ratelimit(key="ip", rate="20/m"), name="create")
class PostViewSet(ViewSet):
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]
    paginator = CustomPagination()

    def _clear_cache(self) -> None:
        clear_cache(settings.redis.prefix.post_list)
        logger.debug("Cache cleared, prefix %s", settings.redis.prefix.post_list)

    @method_decorator(cache_page(60, key_prefix=settings.redis.prefix.post_list))
    def list(self, request: Request) -> Response:
        posts = cast(
            list[Post],
            self.paginator.paginate_queryset(Post.objects.all(), request=request),
        )

        if settings.log.debug_allowed:
            logger.debug("Found %d posts", len(posts))

        result = PostRetrieveSerializer(posts, many=True).data
        return self.paginator.get_paginated_response(result)

    def retrieve(self, _: Request, slug: str) -> Response:
        logger.debug("Fetching post, slug: %r", slug)
        post = Post.objects.get(slug=slug)

        return Response(PostRetrieveSerializer(post).data, HTTP_200_OK)

    def create(self, request: Request) -> Response:
        if settings.log.debug_allowed:
            logger.debug("Creating post, data: %s", str(request.data)[:200])

        cleaned_data = sanitize_data(cast(dict[str, Any], request.data))

        serializer = PostCreateSerializer(data=cleaned_data)
        serializer.is_valid(raise_exception=True)
        logger.debug("Data validated, start saving")

        post = serializer.save(author=request.user)
        logger.info("Post created, id: %s", post.id)

        self._clear_cache()

        return Response(PostRetrieveSerializer(post).data, status=HTTP_201_CREATED)

    def partial_update(self, request: Request, slug: str) -> Response:
        logger.info("Updating post, slug: %s", slug)

        if settings.log.debug_allowed:
            logger.debug("data: %s", str(request.data)[:200])

        cleaned_data = sanitize_data(cast(dict[str, Any], request.data))

        post = Post.objects.get(slug=slug)
        logger.debug("post id: %s", post.id)

        PostService.check_permissions_to_update(post=post, user=request.user)
        logger.debug("Permission checks passed")

        serializer = PostCreateSerializer(
            instance=post, data=cleaned_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        logger.debug("Data validated, start saving")

        post = serializer.save()
        logger.info("Post updated")

        self._clear_cache()

        return Response(PostRetrieveSerializer(post).data, status=HTTP_200_OK)

    def delete(self, request: Request, slug: str) -> Response:
        logger.info("Deleting post, slug: %s", slug)

        post = Post.objects.get(slug=slug)
        logger.info("Post id: %s", post.id)

        PostService.check_permissions_to_delete(post=post, user=request.user)
        logger.debug("Permission checks passed, start deleting")

        post.delete()
        logger.info("Post deleted")

        self._clear_cache()

        return Response(status=HTTP_204_NO_CONTENT)
