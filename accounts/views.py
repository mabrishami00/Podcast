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
