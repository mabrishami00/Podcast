from rest_framework import authentication
import jwt
from django.conf import settings
import datetime
import uuid
from django.core.cache import caches
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from .models import User
import pytz


class JWTAuthentication(authentication.BaseAuthentication):
    jti = str(uuid.uuid4())

    def authenticate(self, request, username=None, password=None):
        authorization_header = request.headers.get("Authorization")
        try:
            jwt_token = JWTAuthentication.get_token_form_header(authorization_header)
        except:
            raise AuthenticationFailed("You are not logged in!")

        if jwt_token is None:
            return None

        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed("Invalid signature")
        except jwt.exceptions.ExpiredSignatureError:
            raise NotAuthenticated("Access Token Expired")
        except Exception as e:
            raise AuthenticationFailed("Invalid token")

        user_id = payload.get("user_id")
        jti = payload.get("jti")

        if user_id is None:
            raise AuthenticationFailed("User identifier not found in JWT")

        if caches["default"].get(jti) is None:
            return None

        user = User.objects.filter(id=user_id).first()

        if user is None:
            raise AuthenticationFailed("User not found")

        return user, payload

    def generate_access_token(self, user):
        access_token_payload = {
            "user_id": user.id,
            "exp": datetime.datetime.now(tz=pytz.timezone("Asia/Tehran"))
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.now(tz=pytz.timezone("Asia/Tehran")),
            "jti": self.jti,
        }
        access_token = jwt.encode(
            access_token_payload, settings.SECRET_KEY, algorithm="HS256"
        )
        return access_token

    def generate_refresh_token(self, user):
        exp = datetime.timedelta(days=7)

        refresh_token_payload = {
            "user_id": user.id,
            "exp": datetime.datetime.now(tz=pytz.timezone("Asia/Tehran")) + exp,
            "iat": datetime.datetime.now(tz=pytz.timezone("Asia/Tehran")),
            "jti": self.jti,
        }
        refresh_token = jwt.encode(
            refresh_token_payload, settings.SECRET_KEY, algorithm="HS256"
        )
        jti = refresh_token_payload.get("jti")
        exp_seconds = exp.total_seconds()

        return refresh_token, jti, exp_seconds

    @classmethod
    def get_token_form_header(cls, token):
        token = token.replace("Bearer", "").replace(" ", "")
        return token
