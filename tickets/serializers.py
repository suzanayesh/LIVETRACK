from django.utils import timezone
from rest_framework import serializers

from tickets.models import Ticket

from .models import Ticket


class BaseTicketCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        exclude = (
            "status",
            "assigned_admin",
            "created_at",
            "updated_at",
            "closed_at",
            "closed_by",
            "is_archived",
        )

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["created_by_admin"] = request.user
        return super().create(validated_data)


class NewUserTicketSerializer(BaseTicketCreateSerializer):
    def create(self, validated_data):
        validated_data["ticket_type"] = "NEW_USER"
        return super().create(validated_data)
# class MaintenanceTicketSerializer(serializers.Serializer):
#     customer_id = serializers.IntegerField()
#     priority = serializers.ChoiceField(
#         choices=["IMPORTANT", "NORMAL"],
#         required=False
#     )
#     availability_time = serializers.CharField(
#         required=False,
#         allow_blank=True
#     )


class TicketResponseSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_type",
            "priority",
            "status",
            "availability_time",
            "created_at",
            "updated_at",
            "closed_at",

            # Snapshot fields
            "customer_full_name",
            "customer_username",
            "customer_password",
            "customer_phone",
            "customer_location",
            "vlan",
            "speed",
            "distributor_name",
            "customer_note",

            "posted_by",
        ]

    def get_posted_by(self, obj):
        return {
            "id": obj.created_by_admin.id,
            "username": obj.created_by_admin.username,
            "role": obj.created_by_admin.role,
        }

class MaintenanceTicketSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    priority = serializers.ChoiceField(
        choices=["IMPORTANT", "NORMAL"],
        required=False
    )
    availability_time = serializers.CharField(
        required=False,
        allow_blank=True
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

class TicketResponseSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_type",
            "priority",
            "status",
            "availability_time",
            "created_at",
            "updated_at",
            "closed_at",
            "is_archived",

            # Snapshot
            "customer_full_name",
            "customer_username",
            "customer_password",
            "customer_phone",
            "customer_location",
            "vlan",
            "speed",
            "distributor_name",
            "customer_note",

            "created_by",
        ]

    def get_created_by(self, obj):
        if not obj.created_by_admin:
            return None
        return {
            "id": obj.created_by_admin.id,
            "username": obj.created_by_admin.username,
            "full_name": obj.created_by_admin.full_name,
            "role": obj.created_by_admin.role,
        }

class TicketCardSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_type",
            "status",
            "priority",
            "created_at",
            "customer_full_name",
            "customer_phone",
            "customer_location",
            "posted_by",
        ]

    def get_posted_by(self, obj):
        if not obj.created_by_admin:
            return None
        return {
            "id": obj.created_by_admin.id,
            "full_name": obj.created_by_admin.full_name,
        }


class TicketUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            "priority",
            "availability_time",
            "assigned_admin",
        ]


class CustomerTicketCardSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = [
            "id",
            "ticket_type",
            "status",
            "priority",
            "created_at",
        ]
