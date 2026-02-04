from django.urls import path

from .views import CommentViewSet

urlpatterns = [
    path(
        "posts/<slug:post_slug>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "posts/<slug:post_slug>/comments/<int:comment_id>/",
        CommentViewSet.as_view({"delete": "delete", "patch": "partial_update"}),
    ),
]
