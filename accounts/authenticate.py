from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        logger.debug(f"Access token from cookie: {token}")

        if not token:
            raise AuthenticationFailed('No access token found in cookies')

        try:
            # If you're using JWT decoding here:
            import jwt
            from django.conf import settings

            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = get_user_model().objects.get(id=payload['user_id'])
            return (user, None)

        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            logger.warning("Token decode failed")
            raise AuthenticationFailed('Invalid token')
        except get_user_model().DoesNotExist:
            logger.warning("User not found from token")
            raise AuthenticationFailed('No such user')

        return None
