import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union

import jwt
from cerberus import Validator
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from social_network.utils import custom_exceptions as ce
from service_auth import schemas
from service_auth.models import User

# Get an instance of logger
logger = logging.getLogger("service_auth")
c_validator = Validator()

# Create DB Session
session = settings.DB_SESSION


class Authentication(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, slug: str) -> Response:
        """
        Handles authentication operations based on the provided slug.

        Parameters:
        request (Request): The request object.
        slug (str): The operation type, e.g., "login" or "regenerate-token".

        Returns:
        Response: A JSON response indicating the outcome of the operation.
        """
        try:
            if slug in ["login", "regenerate-token"]:
                result = handle_authentication(request, slug)
                return result
            else:
                raise ce.InvalidSlug
        except ce.ValidationFailed as vf:
            logger.error("AUTHENTICATION : {}".format(vf))
            return Response(
                {"message": str(vf)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("AUTHENTICATION : {}".format(e))
            return Response(
                {"message": "Internal server error."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def handle_authentication(request, slug: str) -> Response:
    """
    Validates request data and performs login or token regeneration based on the slug.

    Parameters:
    request (Request): The request object.
    slug (str): The operation type, e.g., "login" or "regenerate-token".

    Returns:
    Response: A JSON response indicating the outcome of the operation.
    """
    try:
        if slug == "login":
            is_valid = c_validator.validate(
                request.data, schemas.LOGIN_POST
            )
            if not is_valid:
                raise ce.ValidationFailed(
                    {
                        "message": "Validations Failed.",
                        "data": c_validator.errors,
                    }
                )

            email_address = request.data["email_address"]
            password = request.data["password"]
            password = hashlib.md5(str(password).encode()).hexdigest()

            user = fetch_user(
                email_address=email_address, password=password
            )
            if user:
                access_token = create_access_token(
                    user_code=user["code"]
                )
                refresh_token = create_refresh_token(
                    user_code=user["code"]
                )

                return Response(
                    {
                        "message": "Access granted",
                        "data": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "message": "Access Denied",
                    "data": None,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        elif slug == "regenerate-token":
            is_valid = c_validator.validate(
                request.data, schemas.REGENERATE_TOKEN_POST
            )
            if not is_valid:
                raise ce.ValidationFailed(
                    {
                        "message": "Validations Failed.",
                        "data": c_validator.errors,
                    }
                )
            return regenerate_tokens(
                refresh_token=request.data.get("refresh_token")
            )
    except ce.ValidationFailed as vf:
        logger.error("AUTHENTICATION : {}".format(vf))
        raise
    except Exception as e:
        logger.error("AUTHENTICATION : {}".format(e))
        raise ce.InternalServerError


def create_access_token(user_code: str) -> str:
    """
    Creates an access token for a user.

    Parameters:
    user_code (str): The code of the user.

    Returns:
    str: The generated access token.
    """
    access_token_payload = {
        "user_code": user_code,
        "exp": (
            datetime.now()
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY)
        ),
        "iat": datetime.now(),
    }

    access_token = jwt.encode(
        access_token_payload, settings.SECRET_KEY, algorithm="HS256"
    )

    return access_token


def create_refresh_token(user_code: str) -> str:
    """
    Creates a refresh token for a user.

    Parameters:
    user_code (str): The code of the user.

    Returns:
    str: The generated refresh token.
    """
    refresh_token_payload = {
        "user_code": user_code,
        "exp": (
            datetime.now()
            + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRY)
        ),
        "iat": datetime.now(),
    }

    refresh_token = jwt.encode(
        refresh_token_payload,
        settings.REFRESH_SECRET_KEY,
        algorithm="HS256",
    )

    return refresh_token


def regenerate_tokens(refresh_token: Optional[str] = None) -> Response:
    """
    Regenerates access and refresh tokens using the provided refresh token.

    Parameters:
    refresh_token (Optional[str]): The refresh token.

    Returns:
    Response: A JSON response indicating the outcome of the token regeneration.
    """
    try:
        payload = jwt.decode(
            refresh_token,
            settings.REFRESH_SECRET_KEY,
            algorithms=["HS256"],
        )

        if payload.get("user_code"):
            return Response(
                {
                    "message": "Token regenerated successfully",
                    "data": {
                        "access_token": create_access_token(
                            payload.get("user_code")
                        ),
                        "refresh_token": create_refresh_token(
                            payload.get("user_code")
                        ),
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "Invalid Token",
                "data": None,
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    except jwt.ExpiredSignatureError as e:
        logger.error("REGENERATE TOKEN: {}".format(e))
        return Response(
            {"message": "Token has expired."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    except jwt.InvalidSignatureError as e:
        logger.error("REGENERATE TOKEN: {}".format(e))
        return Response(
            {"message": "Invalid token signature."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    except jwt.DecodeError as e:
        logger.error("REGENERATE TOKEN: {}".format(e))
        return Response(
            {"message": "Token decode error."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    except jwt.InvalidTokenError as e:
        logger.error("REGENERATE TOKEN: {}".format(e))
        return Response(
            {"message": "Invalid token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


def fetch_user(
    user_id: Optional[int] = None,
    user_code: Optional[str] = None,
    email_address: Optional[str] = None,
    name: Optional[str] = None,
    password: Optional[str] = None,
) -> Optional[User]:
    """
    Fetches a user based on provided criteria.

    Parameters:
    user_id (Optional[int]): The ID of the user.
    user_code (Optional[str]): The code of the user.
    email_address (Optional[str]): The email address of the user.
    name (Optional[str]): The name of the user.
    password (Optional[str]): The password of the user.

    Returns:
    Optional[User]: The user object if found, otherwise None.
    """
    try:
        query = session.query(User.code)
        if user_id:
            query = query.filter(User.id == user_id)
        if user_code:
            query = query.filter(User.code == user_code)
        if email_address:
            query = query.filter(User.email_address == email_address)
        if name:
            query = query.filter(User.name == name)
        if password:
            query = query.filter(User.password == password)

        user = query.first()
        session.commit()
    except Exception as e:
        logger.error("FETCH USER: {}".format(e))
        session.rollback()
        user = None

    return user
