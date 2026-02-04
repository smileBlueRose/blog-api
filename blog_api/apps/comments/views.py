from typing import Any, cast

from apps.posts.models import Post
from common.get_required_field import require_field
from common.security import sanitize_html_input
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.viewsets import ViewSet

from .models import Comment
from .serializers import CommentCreateSerializer, CommentRetrieveSerializer


class CommentViewSet(ViewSet):
    def list(self, request: Request, post_slug: str) -> Response:
        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))

        comments = Comment.objects.filter(post__slug=post_slug)[offset : offset + limit]

        return Response(
            CommentRetrieveSerializer(comments, many=True).data, status=HTTP_200_OK
        )

    def create(self, request: Request, post_slug: str) -> Response:
        post = Post.objects.get(slug=post_slug)

        body: str = sanitize_html_input(
            require_field(cast(dict[str, Any], request.data), "body")
        )

        serializer = CommentCreateSerializer(data={"body": body})
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, author=request.user)

        return Response(serializer.data, status=HTTP_201_CREATED)
