from apps.users.models import User
from common.exceptions import PermissionException

from .models import Post


class PostService:
    @staticmethod
    def check_permissions_to_update(post: Post, user: User) -> None:
        """:raises PermissionException:"""

        if not post.author == user:
            raise PermissionException(
                "You don't have enough permissions to update this post"
            )

    @staticmethod
    def check_permissions_to_delete(post: Post, user: User) -> None:
        """:raises PermissionException:"""

        if not post.author == user:
            raise PermissionException(
                "You don't have enough permissions to delete this post"
            )
