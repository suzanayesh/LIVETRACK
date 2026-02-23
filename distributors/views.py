from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Distributor
from .serializers import DistributorSerializer
from livetrack1.services.authorization_service import AuthorizationService


# ---------------------------
# Create Distributor (ROOT only)
# ---------------------------
class DistributorCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not AuthorizationService.is_root(request.user.role):
            return Response(
                {"detail": "Only ROOT can create distributors."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DistributorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ---------------------------
# List All Distributors
# ---------------------------
class DistributorListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Distributor.objects.all().order_by("-created_at")
    serializer_class = DistributorSerializer