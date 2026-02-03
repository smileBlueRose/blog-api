from typing import Any
from uuid import uuid4

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ImageField,
    UUIDField,
)
from django.utils import timezone
from settings.conf import settings


class UserManager(BaseUserManager["User"]):
    def create_user(
        self,
        email: str,
        first_name: str,
        last_name: str,
        raw_password: str,
        **extra_fields: Any,
    ) -> "User":
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(raw_password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            raw_password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    id = UUIDField(primary_key=True, default=uuid4)

    email = EmailField(max_length=settings.users.email_length, unique=True, null=False)
    first_name = CharField(max_length=50, null=False)
    last_name = CharField(max_length=50, null=False)

    is_active = BooleanField(default=True, null=False)
    is_staff = BooleanField(default=False, null=False)

    date_joined = DateTimeField(default=timezone.now)
    avatar = ImageField(upload_to=settings.users.avatars_dir, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self) -> str:
        return self.first_name

    def get_short_name(self) -> str:
        return self.first_name

    def get_full_name(self) -> str:
        return self.first_name + " " + self.last_name

    class Meta:
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"
