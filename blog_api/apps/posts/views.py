from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import ViewSet

from .models import Post
from .serializers import PostSerializer


class PostViewSet(ViewSet):
    def list(self, request: Request) -> Response:

        limit = int(request.query_params.get("limit", 10))
        offset = int(request.query_params.get("offset", 0))

        posts = Post.objects.all()
        posts = posts[offset : offset + limit]

        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data, HTTP_200_OK)

    def retrieve(self, request: Request, pk: int) -> Response:
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post)

            return Response(serializer.data, HTTP_200_OK)

        except Post.DoesNotExist:
            return Response(
                {"error": f"Post with pk '{pk}' not found"}, HTTP_404_NOT_FOUND
            )
