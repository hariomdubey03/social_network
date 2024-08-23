import logging
import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from typing import Optional, Union

from social_network.utils import custom_exceptions as ce
from users.models import User

from social_network.utils.data_formatter import (
    result_list_to_dict,
    result_row_to_dict,
)

# Create DB Session
session = settings.DB_SESSION

# Get an instance of logger
logger = logging.getLogger("service_auth")


class JWTAuthentication(BaseAuthentication):
    """
    JWT authentication class for validating JWT tokens and retrieving the associated user.
    """

    def authenticate(self, request) -> Optional[tuple]:
        """
        Authenticate the request using a JWT token.

        Parameters:
        request (Request): The request object containing the authorization header.

        Returns:
        tuple: A tuple of the user object and None if authentication is successful.
        None: If the authentication header is not present or invalid.
        """
        try:
            authorization_header = request.headers.get("Authorization")
            if authorization_header:
                access_token = authorization_header.split(" ")[1]
                payload = jwt.decode(
                    access_token,
                    settings.SECRET_KEY,
                    algorithms=["HS256"],
                )
                user = fetch_user_by_criteria(
                    user_code=payload.get("user_code")
                )

                if user:
                    return (user, None)

                raise exceptions.NotFound(detail="User not found")

            raise exceptions.AuthenticationFailed(
                "Authorization header missing"
            )

        except jwt.ExpiredSignatureError as e:
            logger.error("AUTHENTICATION : {}".format(e))
            raise ce.ExpiredSignatureError

        except jwt.InvalidSignatureError as e:
            logger.error("AUTHENTICATION : {}".format(e))
            raise ce.InvalidSignatureError

        except jwt.DecodeError as e:
            logger.error("AUTHENTICATION : {}".format(e))
            raise ce.DecodeError

        except jwt.InvalidTokenError as e:
            logger.error("AUTHENTICATION : {}".format(e))
            raise ce.InvalidTokenError


def fetch_user_by_criteria(user_code: str) -> Optional[User]:
    """
    Fetch a user based on provided criteria.

    Parameters:
    user_id (Optional[int]): The ID of the user.
    user_code (Optional[str]): The code of the user.
    name (Optional[str]): The name of the user.
    password (Optional[str]): The password of the user.

    Returns:
    Optional[User]: The user object if found, otherwise None.
    """
    try:
        query = (
            session.query(User.id, User.name, User.code)
            .filter(User.code == user_code)
            .one_or_none()
        )
        session.commit()

        user = result_row_to_dict(query) if query else None
    except Exception as e:
        logger.error("FETCH USER BY CRITERIA: {}".format(e))
        session.rollback()
        user = None

    return user
