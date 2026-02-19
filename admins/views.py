from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admins.serializers import CreateAdminSerializer


class CreateAdminAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != "ROOT":
            return Response(
                {"error": "Only ROOT can create admins"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CreateAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Admin created successfully"},
            status=status.HTTP_201_CREATED
        )
