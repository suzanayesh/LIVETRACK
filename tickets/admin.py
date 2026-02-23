from django.contrib import admin

from tickets.models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = ("id", "ticket_type", "status", "is_archived")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_archived=False)
