from django.db import models


class Ticket(models.Model):

    # =========================
    # Choices
    # =========================
    TICKET_TYPE_CHOICES = [
        ("MAINTENANCE", "Maintenance"),
        ("NEW_USER", "New User"),
    ]

    PRIORITY_CHOICES = [
        ("IMPORTANT", "Important"),
        ("NORMAL", "Normal"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
        ("CLOSED", "Closed"),
    ]

    # =========================
    # Ticket Meta
    # =========================
    ticket_type = models.CharField(
        max_length=20,
        choices=TICKET_TYPE_CHOICES
    )

    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True
    )

    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    assigned_admin = models.ForeignKey(
        "admins.Admin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets"
    )

    created_by_admin = models.ForeignKey(
        "admins.Admin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tickets"
    )

    availability_time = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    is_archived = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    # =========================
    # Customer Snapshot
    # =========================
    customer_full_name = models.CharField(max_length=255)
    customer_username = models.CharField(max_length=150, null=True, blank=True)
    customer_password = models.CharField(max_length=255, null=True, blank=True)
    customer_phone = models.CharField(max_length=20, null=True, blank=True)
    customer_location = models.CharField(max_length=255, null=True, blank=True)

    vlan = models.CharField(max_length=100, null=True, blank=True)
    speed = models.CharField(max_length=50, null=True, blank=True)
    distributor_name = models.CharField(max_length=255, null=True, blank=True)
    customer_note = models.TextField(null=True, blank=True)

    distributor_name = models.CharField(max_length=255, blank=True, null=True)
    customer_note = models.TextField(blank=True, null=True)

    # =========================
    # Closing Info
    # =========================
    closed_at = models.DateTimeField(null=True, blank=True)

    closed_by = models.ForeignKey(
        "admins.Admin",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closed_tickets"
    )

    def __str__(self):
        return f"Ticket #{self.id} - {self.customer_full_name}"
