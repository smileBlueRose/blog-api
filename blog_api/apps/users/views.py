from common.exceptions import MissingRequiredField
from common.security import sanitize_data
from django.forms import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from rest_framework.viewsets import ViewSet

from .exceptions import UserAlreadyExists
from .service import user_service


class UserViewSet(ViewSet):
    def create(self, request: Request) -> Response:
        raw_data = request.data
        if not isinstance(raw_data, dict):
            return Response(
                {"error": "Invalid data format"}, status=HTTP_400_BAD_REQUEST
            )

        try:
            cleaned_data = sanitize_data(raw_data)
        except ValueError:
            return Response(
                {"error": "Invalid data format"}, status=HTTP_400_BAD_REQUEST
            )

        try:
            user = user_service.create_user(cleaned_data)
        except MissingRequiredField as e:
            return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({"error": e.message}, status=HTTP_422_UNPROCESSABLE_ENTITY)
        except UserAlreadyExists as e:
            return Response({"error": str(e)}, status=HTTP_409_CONFLICT)

        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            status=HTTP_201_CREATED,
        )
