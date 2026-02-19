from django.urls import path

from admins.views import CreateAdminAPI

urlpatterns = [
    path("admins/", CreateAdminAPI.as_view(), name="create-admin"),
]
