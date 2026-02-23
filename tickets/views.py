import json

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import Customer
from customers.serializers import CustomerListSerializer
from livetrack1.services.authorization_service import AuthorizationService
from ticket_replies.models import TicketReply, TicketReplyAttachment
from tickets.models import Ticket
from tickets.serializers import TicketCardSerializer, TicketUpdateSerializer
from tickets.services.ticket_service import TicketService

from .serializers import MaintenanceTicketSerializer, TicketResponseSerializer
from .services.ticket_service import TicketService


class NewUserTicketCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket = TicketService.create_new_user_ticket(
            role=request.user.role,
            created_by_admin=request.user,
            customer_data={
                "distributor": request.data.get("distributor"),
                "full_name": request.data.get("full_name"),
                "username": request.data.get("username"),
                "password": request.data.get("password"),
                "phone": request.data.get("phone"),
                "location": request.data.get("location"),
                "vlan": request.data.get("vlan"),
                "speed": request.data.get("speed"),
                "notes": request.data.get("notes"),
            },
            ticket_data={
                "availability_time": request.data.get("availability_time"),
                "note": request.data.get("note"),
            }
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
"created_at": a.created_at,                     }
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

        ticket_data = {
            "id": ticket.id,
            "ticket_type": ticket.ticket_type,
            "status": ticket.status,
            "priority": ticket.priority,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        }

        replies_data = []

        for reply in ticket.replies.all().order_by("created_at"):

            reply_dict = {
                "id": reply.id,
                "status": reply.status,
                "created_at": reply.created_at,
                "performed_by": [
                    {
                        "id": admin.id,
                        "username": admin.username,
                        "full_name": admin.full_name,
                    }
                    for admin in reply.performed_by.all()
                ],
            }

            # optional fields
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
                value = getattr(reply, field)
                if value not in [None, ""]:
                    reply_dict[field] = value

            if reply.attachments.exists():
                reply_dict["attachments"] = [
                    {
                        "id": a.id,
                        "file": a.file.url,
                        "created_at": a.created_at,
                    }
                    for a in reply.attachments.all()
                ]

            replies_data.append(reply_dict)

        return Response({
            "ticket": ticket_data,
            "replies": replies_data
        })





class TicketListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketCardSerializer

    def get_queryset(self):
        return Ticket.objects.all().order_by("-created_at")



class TicketListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketCardSerializer

    def get_queryset(self):
        queryset = Ticket.objects.all().order_by("-created_at")

        status_param = self.request.query_params.get("status")
        priority_param = self.request.query_params.get("priority")

        if status_param:
            queryset = queryset.filter(status=status_param)

        if priority_param:
            queryset = queryset.filter(priority=priority_param)

        return queryset

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
            {
                "message": "Ticket archived successfully",
                "ticket_id": ticket.id,
                "is_archived": ticket.is_archived
            },
            status=status.HTTP_200_OK
        )
    
    

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
            {
                "message": "Ticket updated successfully",
                "ticket_id": ticket.id
            },
            status=status.HTTP_200_OK
        )


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