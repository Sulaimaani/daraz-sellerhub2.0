from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    RefreshTokenCookieView,
    RegisterView,
    UserMeView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenCookieView.as_view(), name="refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserMeView.as_view(), name="me"),
]
