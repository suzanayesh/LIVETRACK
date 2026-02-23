from rest_framework import serializers

from admins.models import Admin
from tickets.serializers import TicketCardSerializer


class CreateAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Admin
        fields = [
            "username",
            "password",
            "full_name",
            "phone",
            "location",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        admin = Admin.objects.create_user(
            **validated_data,
            password=password,
            role="ADMIN",
            is_staff=False,
            is_superuser=False,
        )
        return admin


class AdminProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    role = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    location = serializers.CharField(allow_null=True)
    total_tickets = serializers.IntegerField()
    tickets = TicketCardSerializer(many=True)
    tickets = TicketCardSerializer(many=True)


class AdminListSerializer(serializers.ModelSerializer):
    done_tickets = serializers.IntegerField()

    class Meta:
        model = Admin
        fields = [
            "id",
            "full_name",
            "phone",
            "location",
            "done_tickets",
        ]

class AdminChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)

class AdminUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Admin
        fields = [
            "full_name",
            "phone",
            "location",
            "profile_image",
        ]