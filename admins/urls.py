from django.urls import path

from admins.views import (AdminChangePasswordAPIView, AdminListAPIView,
                          AdminProfileAPIView, AdminUpdateAPIView,
                          CreateAdminAPI, ToggleAdminStatusAPI)

urlpatterns = [
    path("admins/", CreateAdminAPI.as_view(), name="create-admin"),
    path("profile/", AdminProfileAPIView.as_view()),
path("admins/<int:admin_id>/profile/", AdminProfileAPIView.as_view()),
path("admins/list/", AdminListAPIView.as_view()),
    path("admins/<int:admin_id>/toggle-status/", ToggleAdminStatusAPI.as_view(), name="toggle-admin-status"),
    path("admins/<int:admin_id>/change-password/", AdminChangePasswordAPIView.as_view()),
path("admins/<int:admin_id>/update/", AdminUpdateAPIView.as_view()),
]
