import json

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import Customer
from customers.serializers import CustomerSerializer
from ticket_replies.models import TicketReply, TicketReplyAttachment
from tickets.models import Ticket
from tickets.services.ticket_service import TicketService

from .serializers import MaintenanceTicketSerializer, TicketResponseSerializer
from .services.ticket_service import TicketService


class NewUserTicketCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket = TicketService.create_new_user_ticket(
            admin=request.user,
            data=request.data
        )

        serializer = CustomerSerializer(ticket.customer)

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
    

class MaintenanceTicketCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MaintenanceTicketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = TicketService.create_maintenance_ticket(
            role=request.user.role,
            created_by_admin=request.user,
            customer_id=serializer.validated_data["customer_id"],
            ticket_data={
                "priority": serializer.validated_data.get("priority", "NORMAL"),
                "availability_time": serializer.validated_data.get("availability_time"),
                "note": serializer.validated_data.get("note"),
            }
        )

        response_serializer = TicketResponseSerializer(ticket)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class TicketReplyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, pk=pk)

        # ===============================
        # Handle multipart performed_by
        # ===============================
        performed_by_raw = request.data.get("performed_by")

        if not performed_by_raw:
            raise ValidationError(
                "performed_by is required and must contain at least one admin."
            )

        try:
            performed_by_ids = json.loads(performed_by_raw)
        except Exception:
            raise ValidationError("performed_by must be a valid JSON list.")

        # Replace in request data
        data = request.data.copy()
        data["performed_by"] = performed_by_ids

        # ===============================
        # Create Reply via Service
        # ===============================
        reply = TicketService.create_ticket_reply(
            role=request.user.role,
            admin=request.user,
            ticket=ticket,
            data=data,
        )

        # ===============================
        # Handle Attachments (Optional)
        # ===============================
        files = request.FILES.getlist("files")

        attachments_data = []

        for file in files:
            attachment = TicketReplyAttachment.objects.create(
                reply=reply,
                file=file
            )

            attachments_data.append({
                "id": attachment.id,
                "file": attachment.file.url,
"created_at": attachment.created_at,
            })

        # ===============================
        # Build Ticket Data
        # ===============================
        ticket_data = {
            "id": ticket.id,
            "ticket_type": ticket.ticket_type,
            "status": ticket.status,
            "priority": ticket.priority,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        }

        if ticket.closed_at:
            ticket_data["closed_at"] = ticket.closed_at

        if ticket.closed_by:
            ticket_data["closed_by"] = {
                "id": ticket.closed_by.id,
                "username": ticket.closed_by.username,
                "full_name": ticket.closed_by.full_name,
            }

        # ===============================
        # Build Replies Data
        # ===============================
        replies_data = []

        for r in ticket.replies.order_by("created_at"):

            reply_dict = {
                "id": r.id,
                "status": r.status,
                "performed_by": [
                    {
                        "id": admin.id,
                        "username": admin.username,
                        "full_name": admin.full_name,
                    }
                    for admin in r.performed_by.all()
                ],
                "created_at": r.created_at,
            }

            optional_fields = [
                "note",
                "speed_test",
                "username",
                "password",
                "vlan",
                "speed",
                "site_name",
                "device_name",
            ]

            for field in optional_fields:
                value = getattr(r, field)
                if value not in [None, ""]:
                    reply_dict[field] = value

            # Add attachments if exist
            reply_attachments = r.attachments.all()
            if reply_attachments.exists():
                reply_dict["attachments"] = [
                    {
                        "id": a.id,
                        "file": a.file.url,
"created_at": a.created_at,                    }
                    for a in reply_attachments
                ]

            replies_data.append(reply_dict)

        # ===============================
        # Final Response
        # ===============================
        return Response(
            {
                "ticket": ticket_data,
                "replies": replies_data,
            },
            status=status.HTTP_201_CREATED,
        )