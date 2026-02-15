import json
from logging import getLogger
from typing import Any

from django.core.management.base import BaseCommand

from settings.conf import Channels, pubsub

logger = getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Subscribe to Redis comments channel and print incoming comments in real-time"
    )

    def handle(self, *args: Any, **options: Any):
        pubsub.subscribe(Channels.COMMENTS)

        print("Started listening comments...")
        for message in pubsub.listen():
            if (
                message["type"] == "message"
                and message["channel"].decode() == Channels.COMMENTS
            ):
                comment_data = json.loads(message["data"])
                print(comment_data)
