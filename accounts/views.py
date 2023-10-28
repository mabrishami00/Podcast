from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.contrib.auth import logout
from django.conf import settings

from rest_framework import views, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from accounts.serializers import UserLoginSerializer, UserRegisterSerializer
from accounts.backends import JWTAuthentication

from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView, SpectacularRedocView
import jwt

User = get_user_model()

class UserRegisterView(APIView):
    """
    API view for user registration.

    This view allows users to register by providing their registration details.

    Serializer Class: UserRegisterSerializer
    HTTP Methods: POST

    Attributes:
        serializer_class (class): The serializer class for user registration data.
    """

    serializer_class = UserRegisterSerializer

    def post(self, request):
        """
        Handle POST requests for user registration.

        Parameters:
            request (HttpRequest): The HTTP request object containing user registration data.

        Returns:
            Response: A JSON response indicating the success or failure of the registration.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class UserLoginView(APIView):
    """
    API view for user login.

    This view allows users to log in by providing their credentials.

    Serializer Class: UserLoginSerializer
    HTTP Methods: POST

    Attributes:
        serializer_class (class): The serializer class for user login data.
        authentication_classes (list): List of authentication classes for this view.
    """

    serializer_class = UserLoginSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user login.

        Parameters:
            request (HttpRequest): The HTTP request object containing user login data.

        Returns:
            Response: A JSON response containing access and refresh tokens upon successful login.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        user = User.objects.filter(username=username).first()

        if user is None or not user.check_password(password):
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

        access_token = JWTAuthentication.generate_access_token(user)
        refresh_token, jti, exp_seconds = JWTAuthentication.generate_refresh_token(user)

        cache.set(jti, 0, exp_seconds)

        return Response({"access_token": access_token, "refresh_token": refresh_token})

class UserLogoutView(APIView):
    """
    API view for user logout.

    This view allows users to log out, invalidating their refresh token.

    HTTP Methods: POST
    """

    def post(self, request):
        """
        Handle POST requests for user logout.

        Parameters:
            request (HttpRequest): The HTTP request object containing the refresh token payload.

        Returns:
            Response: A JSON response indicating successful or unsuccessful logout.
        """
        payload = request.auth
        try:
            jti = payload.get("jti")
            cache.delete(jti)
        except:
            return Response({"message": "logged out before!"})

        return Response({"message": "logged out successfully!"})

class ObtainNewAccessToken(APIView):
    """
    API view for obtaining a new access token using a refresh token.

    This view allows users to obtain a new access token using their refresh token.

    HTTP Methods: POST
    """

    authentication_classes = []

    def post(self, request):
        """
        Handle POST requests for obtaining a new access token using a refresh token.

        Parameters:
            request (HttpRequest): The HTTP request object containing the refresh token.

        Returns:
            Response: A JSON response containing a new access token and refresh token.
        """
        refresh_token = request.POST.get("refresh").encode("utf-8")
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
        except:
            return Response({"message": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        if cache.get(jti) is None:
            return Response({"message": "Refresh token has been expired!"}, status==status.HTTP_404_NOT_FOUND)
        
        try:
            user_id = payload.get("user_id")
            user = User.objects.get(id=user_id)
        except:
            return Response({"message": "User not found!"}, status==status.HTTP_404_NOT_FOUND)

        cache.delete(jti)
        instance = JWTAuthentication()
        access_token = instance.generate_access_token(user)
        refresh_token, jti, exp_seconds = instance.generate_refresh_token(user)
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        sr_data = ChangePasswordSerializer(data=request.POST)

        if sr_data.is_valid():
            old_password = sr_data.validated_data.get("old_password")
            new_password = sr_data.validated_data.get("new_password")

            if not user.check_password(old_password):
                return Response(
                    "Invalid old password.", status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(new_password)
            user.save()

            publish_uo_message(
                user.id, f"{user.username} has changed the password!", "change_password"
            )

            return Response(
                _("Password changed successfully."), status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    authentication_classes = []
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        sr_data = self.serializer_class(data=request.data)
        if sr_data.is_valid():
            email = sr_data.validated_data["email"]
            try:
                user = User.objects.get(email=email)
            except:
                return Response(_("User not found"), status=status.HTTP_404_NOT_FOUND)

            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = (
                f"{settings.HOST}/accounts/password-reset/confirm/{uidb64}/{token}/"
            )

            recipient_list = [user.email]
            subject = "reset password"
            message = (
                f"You have requested for password reset. Go to this link: {reset_url}."
            )

            sending_email(recipient_list, subject, message)

            return Response(
                _("Password reset email has been sent!"), status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    authentication_classes = []

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            password = generate_random_password()
            user.set_password(password)
            user.save()

            recipient_list = [user.email]
            subject = "Your New Password"
            message = f"Your new password is: {password}"

            sending_email(recipient_list, subject, message)

            return Response(
                _(
                    "New password has been sent to your email. Change it as soon as possible!"
                ),
                status=status.HTTP_200_OK,
            )
        else:
            return Response(_("Invalid token."), status=status.HTTP_400_BAD_REQUEST)


class SpectacularSwaggerView(SpectacularSwaggerView):
    authentication_classes = []

class SpectacularRedocView(SpectacularRedocView):
    authentication_classes = []

class SpectacularAPIView(SpectacularAPIView):
    authentication_classes = []

