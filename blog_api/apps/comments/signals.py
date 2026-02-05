import json
from logging import getLogger
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.signals import post_save
from django.dispatch import receiver
from settings.conf import Channels, redis_client

from .models import Comment
from .serializers import CommentRetrieveSerializer

logger = getLogger(__name__)


@receiver(post_save, sender=Comment)
def comment_created_handler(
    sender: type[Comment], instance: Comment, created: bool, **kwargs: Any
):
    if created:
        serializer = CommentRetrieveSerializer(instance)
        redis_client.publish(
            Channels.COMMENTS, json.dumps(serializer.data, cls=DjangoJSONEncoder)
        )
        logger.debug("Comment published to the channel: %s", Channels.COMMENTS)
