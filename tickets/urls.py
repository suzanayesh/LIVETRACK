from django.urls import path

from tickets.views import TicketListAPIView  # ← أضيفي هذا السطر
from tickets.views import (ArchiveTicketAPIView, MaintenanceTicketCreateView,
                           NewUserTicketCreateView, TicketDetailAPIView,
                           TicketReplyCreateView, UpdateTicketAPIView)

from .views import (DashboardAPIView, MaintenanceTicketCreateView,
                    NewUserTicketCreateView,
                    TicketReplyCreateView)

urlpatterns = [
    path("new-user/", NewUserTicketCreateView.as_view()),
    path("maintenance/", MaintenanceTicketCreateView.as_view()),
    path("tickets/<int:pk>/reply/", TicketReplyCreateView.as_view()),
    path("tickets/<int:pk>/", TicketDetailAPIView.as_view(), name="ticket-detail"),
  path("tickets/", TicketListAPIView.as_view(), name="ticket-list"),
  path("tickets/<int:pk>/update/", UpdateTicketAPIView.as_view(), name="update-ticket"),
path("dashboard/", DashboardAPIView.as_view()),
  path("tickets/<int:pk>/archive/", ArchiveTicketAPIView.as_view(), name="archive-ticket"),
]
