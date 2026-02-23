from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from customers.models import Customer
from customers.serializers import (CreateCustomerSerializer,
                                   CustomerListSerializer,
                                   CustomerListSerializerPhone,
                                   UpdateCustomerSerializer)
from livetrack1.services.authorization_service import AuthorizationService

# ============================================================
# CREATE CUSTOMER
# ============================================================

class CreateCustomerAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not AuthorizationService.can_create_ticket(request.user.role):
            return Response(
                {"error": "Only ADMIN and ROOT can create customers"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CreateCustomerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Customer created successfully"},
            status=status.HTTP_201_CREATED
        )


# ============================================================
# LIST CUSTOMERS
# ============================================================

class ListCustomersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not AuthorizationService.can_create_ticket(request.user.role):
            return Response(
                {"error": "Only ADMIN and ROOT can list customers"},
                status=status.HTTP_403_FORBIDDEN
            )

        customers = Customer.objects.all()
        serializer = CustomerListSerializer(customers, many=True)

        return Response(
            {
                "count": customers.count(),
                "customers": serializer.data
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# LIST CUSTOMERS BY PHONE
# ============================================================

class ListCustomersAPIByPhone(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not AuthorizationService.can_create_ticket(request.user.role):
            return Response(
                {"error": "Only ADMIN and ROOT can list customers"},
                status=status.HTTP_403_FORBIDDEN
            )

        phone = request.query_params.get("phone")
        customers = Customer.objects.all()

        if phone:
            customers = customers.filter(phone__icontains=phone)

        serializer = CustomerListSerializer(customers, many=True)

        return Response(
            {
                "count": customers.count(),
                "customers": serializer.data
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# CUSTOMER DETAIL / UPDATE / DELETE
# ============================================================

class CustomerDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id):
        if not AuthorizationService.can_create_ticket(request.user.role):
            return Response(
                {"error": "Only ADMIN and ROOT can view customers"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CustomerListSerializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, customer_id):
        if not AuthorizationService.can_create_ticket(request.user.role):
            return Response(
                {"error": "Only ADMIN and ROOT can update customers"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateCustomerSerializer(
            customer,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        updated_serializer = CustomerListSerializer(customer)

        return Response(
            {
                "message": "Customer updated successfully",
                "customer": updated_serializer.data
            },
            status=status.HTTP_200_OK
        )

    def delete(self, request, customer_id):

        if not AuthorizationService.is_root(request.user.role):
            return Response(
                {"error": "Only ROOT can delete customers"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        customer.delete()

        return Response(
            {"message": "Customer deleted successfully"},
            status=status.HTTP_200_OK
        )


# ============================================================
# BULK CREATE CUSTOMERS
# ============================================================

class BulkCreateCustomersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not AuthorizationService.can_create_ticket(request.user.role):
            return Response(
                {"error": "Only ADMIN and ROOT can create customers"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of customer objects"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CreateCustomerSerializer(data=request.data, many=True)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        created = serializer.save()
        created_ids = [c.id for c in created]

        return Response(
            {"created": len(created), "ids": created_ids},
            status=status.HTTP_201_CREATED
        )