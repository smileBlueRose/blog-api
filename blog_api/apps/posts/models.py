from apps.users.models import User
from autoslug import AutoSlugField
from django.db.models import (
    CASCADE,
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    TextField,
)
from django.utils import timezone


class Post(Model):
    author = ForeignKey(to=User, on_delete=CASCADE)
    title = CharField(max_length=200, null=False)
    slug = AutoSlugField(populate_from="title", unique=True, max_length=250)
    body = TextField()
    category = ForeignKey("categories.Category", on_delete=SET_NULL, null=True)
    status = CharField(max_length=10)

    created_at = DateTimeField(default=timezone.now)
    updated_at = DateTimeField(default=timezone.now)

    class Meta:
        db_table = "posts"
        verbose_name = "post"
        verbose_name_plural = "posts"
