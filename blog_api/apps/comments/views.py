from typing import Any, cast

from apps.posts.models import Post
from common.get_required_field import require_field
from common.security import sanitize_html_input
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.viewsets import ViewSet

from .models import Comment
from .serializers import CommentCreateSerializer, CommentRetrieveSerializer
from .service import CommentService


class CommentViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "comment_id"

    def _get_post(self, post_slug: str) -> Post:
        return Post.objects.get(slug=post_slug)

    def list(self, request: Request, post_slug: str) -> Response:
        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))

        comments = Comment.objects.filter(post__slug=post_slug)[offset : offset + limit]

        return Response(
            CommentRetrieveSerializer(comments, many=True).data, status=HTTP_200_OK
        )

    def create(self, request: Request, post_slug: str) -> Response:

        body: str = sanitize_html_input(
            require_field(cast(dict[str, Any], request.data), "body")
        )

        serializer = CommentCreateSerializer(data={"body": body})
        serializer.is_valid(raise_exception=True)
        serializer.save(post=self._get_post(post_slug), author=request.user)

        return Response(serializer.data, status=HTTP_201_CREATED)

    def delete(self, request: Request, post_slug: str, comment_id: int) -> Response:
        comment = Comment.objects.get(pk=comment_id)
        if post_slug != comment.post.slug:
            return Response(
                {"error": "Comment doesnt' belong to this post"}, status=404
            )

        CommentService.check_permission_to_delete(user=request.user, comment=comment)

        return Response(status=HTTP_204_NO_CONTENT)
