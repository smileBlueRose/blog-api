from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
)

from apps.categories.models import Category

from .models import Post


class PostCreateSerializer(ModelSerializer):
    category_id = PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category"
    )

    class Meta:
        model = Post
        fields = ("title", "body", "status", "category_id")


class PostRetrieveSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "body",
            "status",
            "created_at",
            "updated_at",
            "author_id",
            "category_id",
        )
