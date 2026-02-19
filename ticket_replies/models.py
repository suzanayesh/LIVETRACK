from django.db import models


class TicketReply(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
        ("CLOSED", "Closed"),
    ]

    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.CASCADE,
        related_name="replies"
    )

    admin = models.ForeignKey(
        "admins.Admin",
        on_delete=models.CASCADE,
        related_name="replies"
    )

    performed_by = models.ManyToManyField(
        "admins.Admin",
        related_name="performed_replies"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    note = models.TextField(null=True, blank=True)

    speed_test = models.TextField(null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    vlan = models.CharField(max_length=100, null=True, blank=True)
    speed = models.CharField(max_length=50, null=True, blank=True)
    site_name = models.CharField(max_length=255, null=True, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Reply #{self.id} - Ticket #{self.ticket.id}"


class TicketReplyAttachment(models.Model):

    reply = models.ForeignKey(
        TicketReply,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(upload_to="ticket_replies/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment {self.id} for Reply {self.reply.id}"
