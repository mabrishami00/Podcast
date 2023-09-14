from rest_framework import authentication
import jwt
from django.conf import settings
import datetime
import uuid
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    jti = str(uuid.uuid4())

    def authenticate(self, request, username=None, password=None):
        authorization_header = request.headers.get("Authorization")
        jwt_token = JWTAuthentication.get_token_form_header(authorization_header)

        if jwt_token is None:
            return None

        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed("Invalid signature")
        except:
            raise AuthenticationFailed("Invalid token")

        user_id = payload.get("user_id")
        jti = payload.get("jti")

        if user_id is None:
            raise AuthenticationFailed("User identifier not found in JWT")

        if cache.get(jti) is None:
            return None

        user = User.objects.filter(id=user_id).first()

        if user is None:
            raise AuthenticationFailed("User not found")

        return user, payload
    @classmethod
    def generate_access_token(cls, user):
        access_token_payload = {
            "user_id": user.id,
            "exp": datetime.datetime.now() + datetime.timedelta(days=0, minutes=5),
            "iat": datetime.datetime.now(),
            "jti": cls.jti,
        }
        access_token = jwt.encode(
            access_token_payload, settings.SECRET_KEY, algorithm="HS256"
        )
        return access_token

    @classmethod
    def generate_refresh_token(cls, user):
        exp = datetime.timedelta(days=7)

        refresh_token_payload = {
            "user_id": user.id,
            "exp": datetime.datetime.now() + exp,
            "iat": datetime.datetime.now(),
            "jti": cls.jti,
        }
        refresh_token = jwt.encode(
            refresh_token_payload, settings.SECRET_KEY, algorithm="HS256"
        )
        jti = refresh_token_payload.get("jti")
        exp_seconds = exp.total_seconds()

        return refresh_token, jti, exp_seconds

