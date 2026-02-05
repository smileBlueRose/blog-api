from logging import getLogger
from typing import Any, Iterable

from common.get_required_field import require_field
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from settings.conf import settings
from zxcvbn import zxcvbn

from .exceptions import UserAlreadyExists
from .models import User

logger = getLogger(__name__)

email_validator = EmailValidator()


class UserService:
    def create_user(self, data: dict[str, Any]) -> User:
        """
        :Raises
            MissingRequiredField:
            UserAlreadyExists:
            ValidationError:
            ValueError: might be raised by sanitize_data()
        """
        fields = ["email", "password", "first_name", "last_name"]
        schema: dict[str, str] = {i: str(require_field(data, i)) for i in fields}
        logger.debug(
            "email: %s, first_name: %s, last_name: %s",
            schema["email"],
            schema["first_name"],
            schema["last_name"],
        )

        email_validator(value=schema["email"])
        logger.debug("Email validated")

        self._check_email_available(email=schema["email"])
        logger.debug("Email available")

        self._validate_first_name(value=schema["first_name"])
        self._validate_last_name(value=schema["last_name"])
        logger.debug("first_name and last_name validated")

        self._validate_password(
            password=schema["password"],
            user_inputs=[v for k, v in schema.items() if k != "password"],
        )
        logger.debug("Password validated")

        user = User.objects.create_user(
            email=schema["email"],
            first_name=schema["first_name"],
            last_name=schema["last_name"],
            raw_password=schema["password"],
        )

        return user

    def _check_email_available(self, email: str) -> None:
        """:raises UserAlreadyExists:"""

        user: User | None = User.objects.filter(email=email).first()

        if user:
            raise UserAlreadyExists(email=email)

    def _validate_password(self, password: str, user_inputs: Iterable[str]) -> None:
        """
        Validates password strength and complexity.

        :param password: Password to validate
        :param user_inputs: User-related strings to check against
        :raises ValidationError: If password is too short, too long, or too weak
        """
        if len(password) < settings.auth.password.min_length:
            raise ValidationError(
                "Password must be at least "
                f"{settings.auth.password.min_length} characters"
            )
        if len(password) > settings.auth.password.max_length:
            raise ValidationError(
                "Password must not exceed "
                f"{settings.auth.password.max_length} characters"
            )

        result = zxcvbn(password, user_inputs=user_inputs)
        entropy = result["guesses_log10"] * 3.32

        if entropy < settings.auth.password.min_entropy:
            feedback_msg = ""

            if result["feedback"]["warning"]:
                feedback_msg = result["feedback"]["warning"]

            if result["feedback"]["suggestions"]:
                feedback_msg += " " + " ".join(result["feedback"]["suggestions"])

            raise ValidationError(
                "Weak password, password strength is "
                f"({entropy:.1f} bits, minimum {settings.auth.password.min_entropy}). "
                f"{feedback_msg}"
            )

    def _validate_first_name(self, value: str) -> None:
        """Validates first name length."""
        if len(value) > settings.users.first_name_max_length:
            raise ValidationError(
                "First name must not exceed "
                f"{settings.users.first_name_max_length} characters"
            )

    def _validate_last_name(self, value: str) -> None:
        """Validates last name length."""
        if len(value) > settings.users.last_name_max_length:
            raise ValidationError(
                "Last name must not exceed "
                f"{settings.users.last_name_max_length} characters"
            )


user_service = UserService()
