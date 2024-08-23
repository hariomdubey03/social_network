import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union
import uuid
import sqlalchemy.exc as alchexc

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.versioning import NamespaceVersioning
from rest_framework.views import APIView

from social_network.utils import custom_exceptions as ce
from social_network.utils.custom_validator import CustomValidator
from social_network.utils.data_formatter import (
    result_list_to_dict,
    result_row_to_dict,
)
from users import schemas
from users.models import User, GroupMembership, SocialGroup

# Get an instance of logger
logger = logging.getLogger("users")

# Get an instance of Custom Validator
c_validator = CustomValidator({}, allow_unknown=True)

# Create DB Session
session = settings.DB_SESSION


class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


class UserAPIView(APIView):
    """
    This is a class for handling CRUD operations on User data.
    Methods
    -------
    post:
    To create a new user instance
    """

    versioning_class = VersioningConfig
    permission_classes = (AllowAny,)

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to dynamically set authentication classes based on request method.
        """
        if request.method in ["GET", "POST"]:
            self.authentication_classes = []

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        """
        Method: GET

        Returns:
        json: List of users or a single user.
        """
        try:
            if request.version == "v1":
                is_valid = c_validator.validate(
                    request.query_params, schemas.USER_GET
                )

                if is_valid:
                    response = retrieve_user(request)
                    return response
                else:
                    raise ce.ValidationFailed(
                        {
                            "message": "Some validations have failed",
                            "data": c_validator.errors,
                        }
                    )
            else:
                raise ce.VersionNotSupported

        except ce.ValidationFailed as vf:
            logger.error("USER API VIEW - GET: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("USER API VIEW - GET: {}".format(vns))
            raise

        except Exception as e:
            logger.error("USER API VIEW - GET: {}".format(e))
            raise ce.InternalServerError

    def post(self, request):
        """
        Method: POST
        Create a new User instance.

        Returns:
        json: Success message.
        """
        try:
            if request.version == "v1":
                is_valid = c_validator.validate(
                    request.data, schemas.USER_POST
                )

                if is_valid:
                    response = create_user_instance(request)
                    return response
                else:
                    raise ce.ValidationFailed(
                        {
                            "message": "Some validations have failed",
                            "data": c_validator.errors,
                        }
                    )
            else:
                raise ce.VersionNotSupported

        except ce.ErrorMSG as em:
            logger.error("USER API VIEW - POST: {}".format(em))
            raise

        except ce.ValidationFailed as vf:
            logger.error("USER API VIEW - POST: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("USER API VIEW - POST: {}".format(vns))
            raise

        except ce.DuplicateKey as dk:
            logger.error("USER API VIEW - POST: {}".format(dk))
            raise

        except Exception as e:
            logger.error("USER API VIEW - POST: {}".format(e))
            raise ce.InternalServerError

    def patch(self, request, group_code):
        """
        Method: PATCH

        Returns:
        json: Success message.
        """
        try:
            if request.version == "v1":
                response = join_group(request, group_code)
                return response
            else:
                raise ce.VersionNotSupported

        except ce.ErrorMSG as em:
            logger.error("USER API VIEW - POST: {}".format(em))
            raise

        except ce.ValidationFailed as vf:
            logger.error("USER API VIEW - POST: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("USER API VIEW - POST: {}".format(vns))
            raise

        except ce.DuplicateKey as dk:
            logger.error("USER API VIEW - POST: {}".format(dk))
            raise

        except Exception as e:
            logger.error("USER API VIEW - POST: {}".format(e))
            raise ce.InternalServerError


def create_user_instance(request) -> Response:
    """
    Create a new user instance from request data.

    Returns:
    Response: Success or error message.
    """
    try:
        name = request.data["name"]
        password = request.data["password"]
        email_address = request.data.get("email_address")

        password = hashlib.md5(str(password).encode()).hexdigest()

        user = insert_user(
            name=name,
            password=password,
            email_address=email_address,
        )
        if user:
            return Response(
                {
                    "message": "User added successfully",
                    "data": {"user_code": user.code},
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "Failed to create user",
                "data": None,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    except ce.ErrorMSG as em:
        logger.error("CREATE USER INSTANCE: {}".format(em))
        raise
    except ce.ValidationFailed as vf:
        logger.error("CREATE USER INSTANCE: {}".format(vf))
        raise
    except Exception as e:
        logger.error("CREATE USER INSTANCE: {}".format(e))
        raise ce.InternalServerError


def retrieve_user(request) -> Response:
    """
    Retrieve user based on request parameters.

    Returns:
    Response: Retrieved user data or error message.
    """
    try:
        user_code = request.query_params.get("user_code")
        email_address = request.query_params.get("email_address")

        user = fetch_user_details(
            user_code=user_code,
            email_address=email_address,
        )
        if user:
            return Response(
                {
                    "message": "User found successfully",
                    "data": user,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "User does not exist",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except ce.ValidationFailed as vf:
        logger.error("RETRIEVE USER: {}".format(vf))
        raise
    except Exception as e:
        logger.error("RETRIEVE USER: {}".format(e))
        raise ce.InternalServerError


def join_group(request, group_code) -> Response:
    """
    Join a group using the provided group code.

    Returns:
    Response: Success or error message.
    """
    try:
        group_membership = insert_group_membership(
            user_id=request.user["id"],
            group_code=group_code,
        )
        if group_membership:
            return Response(
                {
                    "message": "Joined group successfully",
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Unable to join group",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except ce.ErrorMSG as em:
        logger.error("JOIN GROUP: {}".format(em))
        raise
    except ce.ValidationFailed as vf:
        logger.error("JOIN GROUP: {}".format(vf))
        raise
    except Exception as e:
        logger.error("JOIN GROUP: {}".format(e))
        raise ce.InternalServerError


def insert_group_membership(
    user_id: int, group_code: uuid.UUID
) -> Optional[GroupMembership]:
    """
    Insert a new group membership.

    Returns:
    Optional[GroupMembership]: Created GroupMembership or None if failed.
    """
    try:
        group = (
            session.query(SocialGroup)
            .filter(
                SocialGroup.code == group_code,
                SocialGroup.deleted_at.is_(None),
            )
            .one_or_none()
        )
        if not group:
            raise ce.ErrorMSG("Group does not exist")
        if (
            session.query(GroupMembership)
            .filter(
                GroupMembership.user_id == user_id,
                GroupMembership.group_id == group.id,
                GroupMembership.deleted_at.is_(None),
            )
            .first()
        ):
            raise ce.ErrorMSG("Already member of group")

        membership = GroupMembership(
            user_id=user_id,
            group_id=group.id,
        )
        session.add(membership)
        session.commit()

    except ce.ErrorMSG as em:
        logger.error("INSERT GROUP MEMBERSHIP: {}".format(em))
        session.rollback()
        raise
    except Exception as e:
        logger.error("INSERT GROUP MEMBERSHIP: {}".format(e))
        session.rollback()
        membership = None

    return membership


def insert_user(
    name: str,
    password: str,
    email_address: Optional[str] = None,
) -> Optional[User]:
    """
    Insert a new user.

    Returns:
    Optional[User]: Created User or None if failed.
    """
    try:
        user = User(
            name=name,
            email_address=email_address,
            password=password,
        )
        session.add(user)
        session.commit()

    except alchexc.IntegrityError as ie:
        logger.error("NSERT USER: {}".format(ie))
        session.rollback()
        raise ce.ErrorMSG("Duplicate record found for email address")

    except Exception as e:
        logger.error("INSERT USER: {}".format(e))
        session.rollback()
        user = None

    return user


def fetch_user_details(
    user_id: Optional[int] = None,
    user_code: Optional[str] = None,
    name: Optional[str] = None,
    password: Optional[str] = None,
    email_address: Optional[str] = None,
) -> Union[List[User], None]:
    """
    Fetch user details based on filters.

    Returns:
    Optional[User]: User details or None if not found.
    """
    try:
        query = session.query(User.code, User.name, User.email_address)
        if user_id:
            query = query.filter(User.id == user_id)
        if user_code:
            query = query.filter(User.code == user_code)
        if name:
            query = query.filter(User.name == name)
        if password:
            query = query.filter(User.password == password)
        if email_address:
            query = query.filter(User.email_address == email_address)

        user = query.one_or_none()
        session.commit()

        user = result_row_to_dict(user) if user else None

    except Exception as e:
        logger.error("FETCH USER DETAILS: {}".format(e))
        user = None

    return user
