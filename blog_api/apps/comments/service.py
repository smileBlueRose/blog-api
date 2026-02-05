from apps.comments.models import Comment
from apps.users.models import User
from common.exceptions import PermissionException


class CommentService:
    @staticmethod
    def check_permission_to_delete(user: User, comment: Comment) -> None:
        """:raises PermissionException:"""

        if not (user == comment.author):
            raise PermissionException(
                f"User {user.email} doesn't have permissions to delete this comment"
            )

    @staticmethod
    def check_permission_to_update(user: User, comment: Comment) -> None:
        """:raises PermissionException:"""

        if not (user == comment.author):
            raise PermissionException(
                f"User {user.email} doesn't have permissions to update this comment"
            )
