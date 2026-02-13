from logging import getLogger
from typing import Any, cast

from common.get_required_field import require_field
from common.security import sanitize_data
from django.core.files.uploadedfile import UploadedFile
from django.forms import ValidationError
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny, BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from settings.conf import settings

from .models import User
from .serializers import (
    UserCreateSerializer,
    UserRetrieveSerializer,
    UserUpdateSerializer,
)
from .service import user_service

logger = getLogger(__name__)


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST"), name="create")
@method_decorator(
    ratelimit(key="ip", rate="5/m", method="PATCH"), name="partial_update"
)
class UserViewSet(ViewSet):
    lookup_field = "user_id"

    def get_permissions(self) -> list[BasePermission]:
        if self.action == 'partial_update':
            return [IsAuthenticated()]
        return [AllowAny()]
    

    def retrieve(self, _: Request, user_id: str) -> Response:
        logger.info("Retrieve user with user_id: %s", user_id)

        user = User.objects.get(id=user_id)
        return Response(UserRetrieveSerializer(user).data)

    def create(self, request: Request) -> Response:
        logger.info("Creating user")

        if not isinstance(request.data, dict):
            raise ValidationError("Request body must be a JSON object")

        try:
            cleaned_data = sanitize_data(request.data)
        except ValueError as e:
            raise ValidationError(str(e)) from e

        user = user_service.create_user(cleaned_data)

        logger.info("User created")
        return Response(UserCreateSerializer(user).data, status=HTTP_201_CREATED)
    
    def partial_update(self, request: Request) -> Response:
        assert isinstance(request.user, User), "request.user type is not models.User"
        user = request.user

        logger.info("Updating user, user_id: %s", user.id)

        if settings.log.debug_allowed:
            logger.debug("data: %s", str(request.data)[:200])

        cleaned_data = sanitize_data(cast(dict[str, Any], request.data))

        serializer = UserUpdateSerializer(
            instance=user, data=cleaned_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        logger.debug("Data validated, start saving")

        user = serializer.save()
        logger.info("User updated")

        return Response(UserRetrieveSerializer(user).data, status=HTTP_200_OK)


@method_decorator(
    ratelimit(key="ip", rate="5/m", method="PATCH"), name="partial_update"
)
class AvatarViewSet(ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def partial_update(self, request: Request) -> Response:
        # TODO: Make compression of an avatar

        user = request.user
        logger.info("Updating avatar, user_id: %s", user.id)

        avatar_file: UploadedFile = require_field(
            cast(dict[str, UploadedFile], request.FILES), field="avatar"
        )
        logger.debug(
            "Avatar size: %d bytes and filename: %r", avatar_file.size, avatar_file.name
        )

        user_service.validate_avatar(file=avatar_file)
        logger.debug("Avatar validated")

        if user.avatar:
            logger.debug("User already has an avatar, deleting old avatar")
            user.avatar.delete(save=False)

        user.avatar = avatar_file
        user.save()
        logger.info("Avatar saved")

        return Response(status=HTTP_204_NO_CONTENT)
