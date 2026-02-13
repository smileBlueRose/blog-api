from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AvatarViewSet, UserViewSet

router = DefaultRouter()
router.register("", UserViewSet, basename="user")

urlpatterns = [
    path("users/me/", UserViewSet.as_view({"patch": "partial_update"})),
    path("users/me/avatar/", AvatarViewSet.as_view({"patch": "partial_update"})),
    path("users/", include(router.urls)),
]
