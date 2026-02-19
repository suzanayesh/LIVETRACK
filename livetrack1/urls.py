from django.contrib import admin
from django.urls import include, path

from livetrack1.views import LoginAPI

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", LoginAPI.as_view(), name="login"),
    path("api/", include("admins.urls")),
    path("api/", include("tickets.urls")),
path("api/tickets/", include("tickets.urls")),
path("api/distributors/", include("distributors.urls")),
]
