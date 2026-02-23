from rest_framework import serializers
from .models import Customer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from livetrack1.services.authorization_service import AuthorizationService

class CreateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "distributor",
            "full_name",
            "username",
            "password",
            "phone",
            "location",
            "vlan",
            "speed",
            "notes",
        ]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        customer = Customer.objects.create(**validated_data)
        return customer


class CustomerListSerializer(serializers.ModelSerializer):
    distributor_name = serializers.CharField(source="distributor.name", read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "full_name",
            "username",
            "phone",
            "location",
            "vlan",
            "speed",
            "distributor",
            "distributor_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

class CustomerListSerializerPhone(serializers.ModelSerializer):
    distributor_name = serializers.CharField(source="distributor.name", read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",
            "full_name",
            "username",
            "phone",
            "location",
            "vlan",
            "speed",
            "distributor",
            "distributor_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class UpdateCustomerSerializer(serializers.ModelSerializer ):
    class Meta:
        model = Customer
        fields = [
            "distributor",
            "full_name",
            "username",
            "password",
            "phone",
            "location",
            "vlan",
            "speed",
            "notes",
        ]

