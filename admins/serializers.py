from rest_framework import serializers

from admins.models import Admin


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
