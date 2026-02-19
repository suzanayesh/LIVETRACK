from django.contrib.auth.models import AbstractUser
from django.db import models


class Admin(AbstractUser):

    ROLE_CHOICES = [
        ("ROOT", "Root"),
        ("ADMIN", "Admin"),
        ("DISTRIBUTOR", "Distributor"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    profile_image = models.ImageField(
        upload_to="admin_profiles/",
        blank=True,
        null=True
    )

    created_by_root = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_admins"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
