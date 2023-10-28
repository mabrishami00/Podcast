from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path(
        "logout_all_sessions/",
        views.LogoutAllSessions.as_view(),
        name="logout_all_sessions",
    ),
    path("refresh/", views.ObtainNewAccessToken.as_view(), name="refresh"),
    path(
        "change_password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
