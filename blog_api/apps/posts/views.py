from typing import Any, cast

from common.exceptions import PermissionException
from common.security import sanitize_data
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)
from rest_framework.viewsets import ViewSet

from .models import Post
from .serializers import PostCreateSerializer, PostRetrieveSerializer
from .service import PostService


class PostViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request: Request) -> Response:
        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))

        posts = Post.objects.all()[offset : offset + limit]

        return Response(PostRetrieveSerializer(posts, many=True).data, HTTP_200_OK)

    def retrieve(self, request: Request, pk: int) -> Response:
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"error": f"Post with pk '{pk}' not found"}, HTTP_404_NOT_FOUND
            )
        return Response(PostRetrieveSerializer(post).data, HTTP_200_OK)

    def create(self, request: Request) -> Response:
        cleaned_data = sanitize_data(cast(dict[str, Any], request.data))

        serializer = PostCreateSerializer(data=cleaned_data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user)

        return Response(PostRetrieveSerializer(post).data, status=HTTP_201_CREATED)

    def partial_update(self, request: Request, pk: int) -> Response:
        cleaned_data = sanitize_data(cast(dict[str, Any], request.data))

        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"error": f"Post with pk '{pk}' not found"}, HTTP_404_NOT_FOUND
            )
        try:
            PostService.check_permissions_to_update(post=post, user=request.user)
        except PermissionException as e:
            return Response({"error": str(e)}, status=HTTP_403_FORBIDDEN)

        serializer = PostCreateSerializer(
            instance=post, data=cleaned_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        return Response(PostRetrieveSerializer(post).data, status=HTTP_200_OK)

    def delete(self, request: Request, pk: int) -> Response:
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"error": f"Post with pk '{pk}' not found"}, HTTP_404_NOT_FOUND
            )

        try:
            PostService.check_permissions_to_delete(post=post, user=request.user)
        except PermissionException as e:
            return Response({"error": str(e)}, status=HTTP_403_FORBIDDEN)

        post.delete()

        return Response(status=HTTP_204_NO_CONTENT)
