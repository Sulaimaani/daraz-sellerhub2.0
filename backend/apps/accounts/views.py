from django.conf import settings
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import User
from .serializers import RegisterSerializer, UserSerializer


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
        httponly=True,
        secure=getattr(settings, "SESSION_COOKIE_SECURE", False),
        samesite="Lax",
        path="/api/auth/refresh/",
        domain=settings.REFRESH_COOKIE_DOMAIN,
    )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        # Here we would also send a verification email with a token

        headers = self.get_success_headers(serializer.data)
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save()


class LoginView(TokenObtainPairView):
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh_token = response.data.get("refresh")
            if refresh_token:
                set_refresh_cookie(response, refresh_token)
                # Remove refresh token from response body
                del response.data["refresh"]
        return response


class RefreshTokenCookieView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.data["refresh"] = refresh_token

        try:
            response = super().post(request, *args, **kwargs)
        except InvalidToken as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        if response.status_code == 200:
            new_refresh = response.data.get("refresh")
            if new_refresh:
                set_refresh_cookie(response, new_refresh)
                del response.data["refresh"]
        return response


class LogoutView(views.APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            response = Response(status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie(
                "refresh_token",
                path="/api/auth/refresh/",
                domain=settings.REFRESH_COOKIE_DOMAIN,
            )
            return response
        except TokenError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserMeView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
