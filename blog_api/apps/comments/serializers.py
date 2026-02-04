from rest_framework.serializers import ModelSerializer

from .models import Comment


class CommentRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ("post_id", "author_id", "body", "created_at")


class CommentCreateSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ("body",)
