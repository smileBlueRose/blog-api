from logging import getLogger

from common.security import sanitize_data
from django.forms import ValidationError
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
)
from rest_framework.viewsets import ViewSet

from .serializers import UserSerializer
from .service import user_service

logger = getLogger(__name__)


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST"), name="create")
class UserViewSet(ViewSet):
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
        return Response(UserSerializer(user).data, status=HTTP_201_CREATED)
