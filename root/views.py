from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from livetrack1.services.auth_service import AuthenticationService


class LoginAPIView(APIView):

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = AuthenticationService.login(username, password)

            user = result["user"]
            role = result["role"]

            return Response({
                "message": "Login successful",
                "role": role,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": getattr(user, "full_name", None),
                }
            })

        except ValueError:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
