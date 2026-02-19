from django.urls import path

from .views import (MaintenanceTicketCreateView, NewUserTicketCreateView,
                    TicketReplyCreateView)

urlpatterns = [
    path("new-user/", NewUserTicketCreateView.as_view()),
    path("maintenance/", MaintenanceTicketCreateView.as_view()),
    path("tickets/<int:pk>/reply/", TicketReplyCreateView.as_view()),
]
