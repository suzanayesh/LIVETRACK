from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from admins.models import Admin
from admins.serializers import \
    AdminChangePasswordSerializer  # ← أضيفي هذا السطر
from admins.serializers import AdminListSerializer  # ← أضيفي هذا السطر
from admins.serializers import (AdminProfileSerializer, AdminUpdateSerializer,
                                CreateAdminSerializer)
from livetrack1.services.authorization_service import AuthorizationService
from tickets.services.ticket_service import TicketService

from .serializers import AdminListSerializer, AdminProfileSerializer

# ============================================================
# Create Admin (ROOT only)
# ============================================================

class CreateAdminAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not AuthorizationService.can_create_admin(request.user.role):
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


# ============================================================
# Activate / Deactivate Admin (ROOT only)
# ============================================================

class ToggleAdminStatusAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, admin_id):

        if not AuthorizationService.can_manage_admins(request.user.role):
            return Response(
                {"error": "Only ROOT can modify admin status"},
                status=status.HTTP_403_FORBIDDEN
            )

        admin = get_object_or_404(Admin, id=admin_id)

        # ❌ لا يمكن إيقاف ROOT
        if admin.role == "ROOT":
            return Response(
                {"error": "You cannot deactivate a ROOT account"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ❌ لا يمكن إيقاف نفسك
        if admin.id == request.user.id:
            return Response(
                {"error": "You cannot deactivate yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        admin.is_active = not admin.is_active
        admin.save(update_fields=["is_active"])

        return Response(
            {
                "message": "Admin status updated successfully",
                "admin_id": admin.id,
                "is_active": admin.is_active
            },
            status=status.HTTP_200_OK
        )


class AdminProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, admin_id=None):

        # لو فيه admin_id → فقط ROOT مسموح
        if admin_id:
            if not AuthorizationService.is_root(request.user.role):
                return Response(
                    {"error": "Only ROOT can view other admins"},
                    status=status.HTTP_403_FORBIDDEN
                )
            admin = get_object_or_404(Admin, id=admin_id)
        else:
            admin = request.user

        data = TicketService.get_admin_profile_data(admin)

        serializer = AdminProfileSerializer({
            "id": admin.id,
            "username": admin.username,
            "full_name": admin.full_name,
            "role": admin.role,
            "phone": admin.phone,
            "location": admin.location,
            "total_tickets": data["total_tickets"],
            "tickets": data["tickets"],
        })

        return Response(serializer.data)
    
class AdminListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not AuthorizationService.is_root(request.user.role):
            return Response(
                {"error": "Only ROOT can view admin list"},
                status=status.HTTP_403_FORBIDDEN
            )

        admins = TicketService.get_admins_with_done_count()
        serializer = AdminListSerializer(admins, many=True)

        return Response(serializer.data)
    

class AdminChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, admin_id):

        if not AuthorizationService.is_root(request.user.role):
            return Response(
                {"error": "Only ROOT can change admin passwords"},
                status=status.HTTP_403_FORBIDDEN
            )

        admin = get_object_or_404(Admin, id=admin_id)

        serializer = AdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        admin.set_password(serializer.validated_data["new_password"])
        admin.save(update_fields=["password"])

        return Response({"message": "Password updated successfully"})
    
class AdminUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, admin_id):

        if not AuthorizationService.is_root(request.user.role):
            return Response(
                {"error": "Only ROOT can update admins"},
                status=status.HTTP_403_FORBIDDEN
            )

        admin = get_object_or_404(Admin, id=admin_id)

        serializer = AdminUpdateSerializer(
            admin,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Admin updated successfully"
        })