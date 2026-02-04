from typing import Any

from apps.users.exceptions import UserAlreadyExists
from common.exceptions import MissingRequiredField
from django.forms import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(
    exc: Exception, context: dict[str, Any]
) -> Response | None:
    response = exception_handler(exc, context)

    if isinstance(exc, MissingRequiredField):
        return Response({"error": f"Missing required field: {exc.field}"}, status=400)

    if isinstance(exc, ValidationError):
        return Response({"error": exc.message}, status=422)

    if isinstance(exc, UserAlreadyExists):
        return Response({"error": str(exc)}, status=409)

    return response
