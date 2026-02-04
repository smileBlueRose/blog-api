from typing import ClassVar, Self

from django.db.models import (
    CASCADE,
    DateTimeField,
    ForeignKey,
    Manager,
    Model,
    TextField,
)
from django.utils import timezone


class Comment(Model):
    post = ForeignKey("posts.Post", on_delete=CASCADE)
    author = ForeignKey("users.User", on_delete=CASCADE)
    body = TextField()
    created_at = DateTimeField(default=timezone.now)

    class Meta:
        db_table = "comments"
        verbose_name = "comment"
        verbose_name_plural = "comments"

    objects: ClassVar[Manager[Self]]
