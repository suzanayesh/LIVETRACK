from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from livetrack1.services.auth_service import AuthService


class LoginAPI(APIView):
    permission_classes = []  # Public endpoint

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = AuthService.login(username, password)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
