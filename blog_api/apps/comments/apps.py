from django.apps import AppConfig


class CommentsConfig(AppConfig):
    name = "apps.comments"

    def ready(self) -> None:
        from .signals import comment_created_handler  # noqa: F401

        return super().ready()
