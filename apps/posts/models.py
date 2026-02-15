from typing import ClassVar, Self

from autoslug import AutoSlugField

from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    Manager,
    Model,
    TextField,
)
from django.utils import timezone

from apps.users.models import User
from settings.conf import settings

from .enums import StatusEnum


class Post(Model):
    id: int
    author = ForeignKey(to=User, on_delete=CASCADE)
    title = CharField(max_length=settings.post.title_max_length, null=False)
    slug = AutoSlugField(populate_from="title", unique=True, max_length=250)
    body = TextField()
    category = ForeignKey("categories.Category", on_delete=SET_NULL, null=True)
    status = CharField(max_length=10, choices=[(i.value, i.value) for i in StatusEnum])

    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)

    class Meta:
        db_table = "posts"
        verbose_name = "post"
        verbose_name_plural = "posts"

    objects: ClassVar[Manager[Self]]
