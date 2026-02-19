from django.db import models


class Customer(models.Model):
    distributor = models.ForeignKey(
        "distributors.Distributor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers"
    )

    full_name = models.CharField(max_length=255)

    username = models.CharField(
    max_length=150,
    null=True,
    blank=True
)

    password = models.CharField(
    max_length=255,
    null=True,
    blank=True
)


    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=255)

    vlan = models.CharField(max_length=100, blank=True, null=True)
    speed = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
