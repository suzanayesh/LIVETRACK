from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Admin


@admin.register(Admin)
class AdminUserAdmin(UserAdmin):
    model = Admin

    list_display = ("username", "email", "role", "is_staff")

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": (
                "role",
                "full_name",
                "phone",
                "location",
                "profile_image",
                "created_by_root",
            )
        }),
    )
