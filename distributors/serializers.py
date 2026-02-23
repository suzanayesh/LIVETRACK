from rest_framework import serializers
from .models import Distributor


class DistributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distributor
        fields = ["id", "name", "area", "created_at"]
        read_only_fields = ["id", "created_at"]