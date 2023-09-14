from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.contrib.auth import logout
from django.conf import settings

from rest_framework import views, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

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
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti")
        cache.get(jti)
        user_id = payload.get("user_id")
        user = User.objects.get(id=user_id)
        cache.delete(jti)
        access_token = JWTAuthentication.generate_access_token(user)
        refresh_token, jti, exp_seconds = JWTAuthentication.generate_refresh_token(user)
        cache.set(jti, 0, exp_seconds)
        return Response({"access_token": access_token, "refresh_token": refresh_token})

class SpectacularSwaggerView(SpectacularSwaggerView):
    authentication_classes = []

class SpectacularRedocView(SpectacularRedocView):
    authentication_classes = []

class SpectacularAPIView(SpectacularAPIView):
    authentication_classes = []

