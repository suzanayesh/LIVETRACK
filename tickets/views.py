import json

import django_filters
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.serializers import CustomerListSerializer
from livetrack1.services.authorization_service import AuthorizationService
from ticket_replies.models import TicketReplyAttachment
from tickets.models import Ticket
from tickets.serializers import TicketCardSerializer, TicketUpdateSerializer
from tickets.services.ticket_service import TicketService

from .serializers import MaintenanceTicketSerializer, TicketResponseSerializer

# ============================================================
# Filtering
# ============================================================

class TicketFilter(django_filters.FilterSet):

    created_from = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="gte"
    )

    created_to = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="lte"
    )

    class Meta:
        model = Ticket
        fields = ["status", "priority", "ticket_type"]


# ============================================================
# Pagination
# ============================================================

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# ============================================================
# CREATE NEW USER
# ============================================================

class NewUserTicketCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket = TicketService.create_new_user_ticket(
            role=request.user.role,
            created_by_admin=request.user,
            customer_data=request.data,
            ticket_data=request.data
        )

        serializer = CustomerListSerializer(ticket.customer)

        return Response(
            {
                "ticket_id": ticket.id,
                "created_by": {
                    "id": ticket.created_by_admin.id,
                    "username": ticket.created_by_admin.username,
                    "full_name": ticket.created_by_admin.full_name,
                    "role": ticket.created_by_admin.role,
                },
                "customer_profile": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


# ============================================================
# CREATE MAINTENANCE
# ============================================================

class MaintenanceTicketCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MaintenanceTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = TicketService.create_maintenance_ticket(
            role=request.user.role,
            created_by_admin=request.user,
            customer_id=serializer.validated_data["customer_id"],
            ticket_data=serializer.validated_data
        )

        return Response(
            TicketResponseSerializer(ticket).data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# REPLY
# ============================================================

class TicketReplyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        performed_by_raw = request.data.get("performed_by")

        if not performed_by_raw:
            raise ValidationError("performed_by is required")

        try:
            performed_by_ids = json.loads(performed_by_raw)
        except Exception:
            raise ValidationError("performed_by must be a valid JSON list.")

        data = request.data.copy()
        data["performed_by"] = performed_by_ids

        reply = TicketService.create_ticket_reply(
            role=request.user.role,
            admin=request.user,
            ticket=ticket,
            data=data,
        )

        files = request.FILES.getlist("files")

        for file in files:
            TicketReplyAttachment.objects.create(
                reply=reply,
                file=file
            )

        return Response(
            {"message": "Reply created successfully"},
            status=status.HTTP_201_CREATED,
        )


# ============================================================
# DETAIL
# ============================================================

class TicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        ticket = get_object_or_404(
            Ticket.objects.prefetch_related(
                "replies__performed_by",
                "replies__attachments"
            ),
            pk=pk
        )

        return Response(TicketResponseSerializer(ticket).data)


# ============================================================
# LIST (Production Level)
# ============================================================

class TicketListAPIView(ListAPIView):
    serializer_class = TicketResponseSerializer
    queryset = Ticket.objects.select_related(
        "customer",
        "created_by_admin"
    ).order_by("-created_at")

    pagination_class = StandardResultsSetPagination

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = TicketFilter

    search_fields = [
        "customer_full_name",
        "customer_phone",
        "customer_username",
    ]

    ordering_fields = [
        "created_at",
        "status",
        "priority",
    ]

    ordering = ["-created_at"]


# ============================================================
# ARCHIVE
# ============================================================

class ArchiveTicketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        if not AuthorizationService.is_root(request.user.role):
            return Response(
                {"error": "Only ROOT can archive tickets"},
                status=status.HTTP_403_FORBIDDEN
            )

        ticket = get_object_or_404(Ticket, pk=pk)

        ticket.is_archived = True
        ticket.save(update_fields=["is_archived"])

        return Response(
            {"message": "Ticket archived successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================
# UPDATE
# ============================================================

class UpdateTicketAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        if not AuthorizationService.is_root(request.user.role):
            return Response(
                {"error": "Only ROOT can update tickets"},
                status=status.HTTP_403_FORBIDDEN
            )

        ticket = get_object_or_404(Ticket, pk=pk)

        serializer = TicketUpdateSerializer(
            ticket,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Ticket updated successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================
# DASHBOARD
# ============================================================

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = TicketService.get_dashboard_data()

        return Response({
            "stats": data["stats"],
            "recent_tickets": TicketCardSerializer(
                data["recent"],
                many=True
            ).data
        })