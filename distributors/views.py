from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from livetrack1.services.authorization_service import AuthorizationService

from .models import Distributor
from .serializers import DistributorSerializer


class DistributorCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not AuthorizationService.is_root(request.user):
            return Response(
                {"detail": "Only ROOT can create distributors."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = DistributorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
