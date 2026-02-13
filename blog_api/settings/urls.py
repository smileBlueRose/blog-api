from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .base import DEBUG, MEDIA_ROOT, MEDIA_URL

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.users.urls_auth")),
    path("api/", include("apps.posts.urls")),
    path("api/", include("apps.comments.urls")),
    path("api/", include("apps.users.urls")),
]


if DEBUG:
    urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)  # type: ignore
