import logging

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from admins.models import Admin
from customers.models import Customer
from distributors.models import Distributor
from livetrack1.services.authorization_service import AuthorizationService
from ticket_replies.models import TicketReply
from tickets.models import Ticket

logger = logging.getLogger("tickets")


class TicketService:

    # ============================================================
    # CREATE NEW USER TICKET
    # ============================================================

    @staticmethod
    def create_new_user_ticket(
        *,
        role: str,
        created_by_admin,
        customer_data: dict,
        ticket_data: dict
    ) -> Ticket:

        if not AuthorizationService.can_create_ticket(role):
            raise PermissionDenied("Not allowed to create tickets")

        distributor = Distributor.objects.get(id=customer_data["distributor"])

        customer = Customer.objects.create(
            distributor=distributor,
            full_name=customer_data["full_name"],
            username=customer_data.get("username"),
            password=customer_data.get("password"),
            phone=customer_data["phone"],
            location=customer_data["location"],
            vlan=customer_data.get("vlan"),
            speed=customer_data.get("speed"),
            notes=customer_data.get("notes"),
        )

        ticket = Ticket.objects.create(
            ticket_type="NEW_USER",
            priority="IMPORTANT",
            status="PENDING",
            customer=customer,
            created_by_admin=created_by_admin,
            availability_time=ticket_data.get("availability_time"),
            is_archived=False,

            customer_full_name=customer.full_name,
            customer_username=customer.username,
            customer_password=customer.password,
            customer_phone=customer.phone,
            customer_location=customer.location,
            vlan=customer.vlan,
            speed=customer.speed,
            distributor_name=customer.distributor.name if customer.distributor else None,
            customer_note=ticket_data.get("note"),
        )

        return ticket

    # ============================================================
    # CREATE MAINTENANCE TICKET
    # ============================================================

    @staticmethod
    def create_maintenance_ticket(
        *,
        role: str,
        created_by_admin,
        customer_id: int,
        ticket_data: dict
    ) -> Ticket:

        if not AuthorizationService.can_create_ticket(role):
            raise PermissionDenied("Not allowed to create tickets")

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Customer does not exist")

        note_value = ticket_data.get("note") or None

        ticket = Ticket.objects.create(
            ticket_type="MAINTENANCE",
            priority=ticket_data.get("priority", "NORMAL"),
            status="PENDING",
            customer=customer,
            created_by_admin=created_by_admin,
            availability_time=ticket_data.get("availability_time"),
            is_archived=False,

            customer_full_name=customer.full_name,
            customer_username=customer.username,
            customer_password=customer.password,
            customer_phone=customer.phone,
            customer_location=customer.location,
            vlan=customer.vlan,
            speed=customer.speed,
            distributor_name=customer.distributor.name if customer.distributor else None,
            customer_note=note_value,
        )

        return ticket

    # ============================================================
    # CREATE REPLY (Unified Reply + Status Update)
    # ============================================================

    @staticmethod
    def create_ticket_reply(
        *,
        role: str,
        admin,
        ticket,
        data: dict
    ):

        performed_by_ids = data.get("performed_by")

        if not performed_by_ids or not isinstance(performed_by_ids, list):
            raise ValidationError(
                "performed_by is required and must contain at least one admin."
            )

        performers = Admin.objects.filter(id__in=performed_by_ids)

        if performers.count() != len(performed_by_ids):
            raise ValidationError(
                "One or more admins in performed_by do not exist."
            )

        new_status = data.get("status") or ticket.status

        allowed_statuses = [
            "PENDING",
            "ACCEPTED",
            "IN_PROGRESS",
            "DONE",
            "CLOSED",
        ]

        if new_status not in allowed_statuses:
            raise ValidationError("Invalid status value.")

        if ticket.status == "CLOSED":
            raise PermissionDenied("This ticket is already closed.")

        if role == "ADMIN":
            allowed_transitions = {
                "PENDING": ["ACCEPTED"],
                "ACCEPTED": ["IN_PROGRESS"],
                "IN_PROGRESS": ["DONE"],
                "DONE": [],
            }

            if new_status != ticket.status:
                if new_status not in allowed_transitions.get(ticket.status, []):
                    raise PermissionDenied(
                        f"Invalid status transition from {ticket.status} to {new_status}."
                    )

        if new_status == "CLOSED" and role != "ROOT":
            raise PermissionDenied(
                "Only ROOT users are allowed to close tickets."
            )

        # ===============================
        # Update ticket status + Logging
        # ===============================
        if new_status != ticket.status:
            old_status = ticket.status
            ticket.status = new_status
            ticket.save(update_fields=["status", "updated_at"])

            logger.info(
                f"Ticket {ticket.id} status changed "
                f"from {old_status} to {new_status} "
                f"by {admin.username}"
            )

            if new_status == "CLOSED":
                ticket.closed_at = timezone.now()
                ticket.closed_by = admin
                ticket.save(update_fields=["closed_at", "closed_by"])

                logger.info(
                    f"Ticket {ticket.id} closed by {admin.username}"
                )

        reply = TicketReply.objects.create(
            ticket=ticket,
            admin=admin,
            status=new_status,
            note=data.get("note"),
            speed_test=data.get("speed_test"),
            username=data.get("username"),
            password=data.get("password"),
            vlan=data.get("vlan"),
            speed=data.get("speed"),
            site_name=data.get("site_name"),
            device_name=data.get("device_name"),
        )

        reply.performed_by.set(performers)

        return reply

    # ============================================================
    # ADMIN PROFILE DATA
    # ============================================================

    @staticmethod
    def get_admin_profile_data(admin):

        tickets = Ticket.objects.filter(
            Q(created_by_admin=admin) |
            Q(replies__performed_by=admin)
        ).distinct().order_by("-created_at")

        return {
            "admin": admin,
            "tickets": tickets,
            "total_tickets": tickets.count(),
        }

    # ============================================================
    # DASHBOARD DATA
    # ============================================================

    @staticmethod
    def get_dashboard_data():

        stats = Ticket.objects.aggregate(
            pending=Count("id", filter=Q(status="PENDING")),
            accepted=Count("id", filter=Q(status="ACCEPTED")),
            in_progress=Count("id", filter=Q(status="IN_PROGRESS")),
            done=Count("id", filter=Q(status="DONE")),
        )

        recent_tickets = Ticket.objects.filter(
            status="PENDING"
        ).order_by("-created_at")[:6]

        return {
            "stats": stats,
            "recent": recent_tickets,
        }