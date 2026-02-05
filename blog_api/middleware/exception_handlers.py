from logging import getLogger
from typing import Any

from apps.users.exceptions import UserAlreadyExists
from common.exceptions import MissingRequiredField, PermissionException
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError
from django_ratelimit.exceptions import Ratelimited
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from rest_framework.views import exception_handler

logger = getLogger(__name__)


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    response = exception_handler(exc, context)

    if isinstance(exc, MissingRequiredField):
        return Response(
            {"error": f"Missing required field: {exc.field}"},
            status=HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, ValidationError):
        return Response({"error": exc.message}, status=HTTP_422_UNPROCESSABLE_ENTITY)

    if isinstance(exc, UserAlreadyExists):
        return Response({"error": str(exc)}, status=HTTP_409_CONFLICT)

    if isinstance(exc, ObjectDoesNotExist):
        model_name = exc.__class__.__qualname__.replace(".DoesNotExist", "")
        return Response({"error": f"{model_name} not found"}, status=HTTP_404_NOT_FOUND)

    if isinstance(exc, PermissionException):
        return Response({"error": str(exc)}, status=HTTP_403_FORBIDDEN)

    if isinstance(exc, Ratelimited):
        request = context["request"]
        ip = request.META.get("REMOTE_ADDR")
        logger.warning(
            f"User with IP {ip} was blocked. "
            f"Rate limit exceeded for {request.method} {request.path}"
        )
        return response

    return response
