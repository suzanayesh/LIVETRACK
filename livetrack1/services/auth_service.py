from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class AuthService:

    @staticmethod
    def login(username: str, password: str):
        user = authenticate(username=username, password=password)

        if not user:
            raise Exception("Invalid credentials")

        if not user.is_active:
            raise Exception("User is inactive")

        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "username": user.username,
        }
