import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union
import sqlalchemy.exc as alchexc

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.versioning import NamespaceVersioning
from rest_framework.views import APIView
from sqlalchemy import and_

from social_network.utils import custom_exceptions as ce
from social_network.utils.custom_validator import CustomValidator
from social_network.utils.data_formatter import (
    result_list_to_dict,
    result_row_to_dict,
)
from operations import schemas
from operations.models import GroupMembership, SocialGroup, User

# Get an instance of logger
logger = logging.getLogger("operations")

# Get an instance of Custom Validator
c_validator = CustomValidator({}, allow_unknown=True)


class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


# Create DB Session
session = settings.DB_SESSION


class SocialGroupsAPIView(APIView):
    """
    Handles CRUD operations for Social Group data, including retrieving, creating, and deleting social groups.
    """

    versioning_class = VersioningConfig
    permission_classes = (AllowAny,)

    def get(self, request):
        """
        Retrieves existing Social Groups or a specific group based on the provided unique group code.

        Returns a list of groups or details of a single group.
        """
        try:
            if request.version == "v1":
                is_valid = c_validator.validate(
                    request.query_params, schemas.GROUP_GET
                )

                if is_valid:
                    response = retrieve_group(request)
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
            logger.error("SOCIAL GROUP API VIEW - GET: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("SOCIAL GROUP API VIEW - GET: {}".format(vns))
            raise

        except Exception as e:
            logger.error("SOCIAL GROUP API VIEW - GET: {}".format(e))
            raise ce.InternalServerError

    def post(self, request):
        """
        Creates a new Social Group instance based on the provided data.

        Returns a success message if the group is created successfully.
        """
        try:
            if request.version == "v1":
                is_valid = c_validator.validate(
                    request.data, schemas.GROUP_POST
                )

                if is_valid:
                    response = create_group_instance(request)
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
            logger.error("SOCIAL GROUP API VIEW - POST: {}".format(em))
            raise
        except ce.ValidationFailed as vf:
            logger.error("SOCIAL GROUP API VIEW - POST: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("SOCIAL GROUP API VIEW - POST: {}".format(vns))
            raise

        except ce.DuplicateKey as dk:
            logger.error("SOCIAL GROUP API VIEW - POST: {}".format(dk))
            raise

        except Exception as e:
            logger.error("SOCIAL GROUP API VIEW - POST: {}".format(e))
            raise ce.InternalServerError

    def delete(self, request, group_code):
        """
        Deletes an existing Social Group based on the provided group code.

        Returns a success message if the group is deleted successfully.
        """
        try:
            if request.version == "v1":

                response = delete_group_instance(group_code)
                return response
            else:
                raise ce.VersionNotSupported

        except ce.ValidationFailed as vf:
            logger.error(
                "SOCIAL GROUP API VIEW - DELETE: {}".format(vf)
            )
            raise

        except ce.VersionNotSupported as vns:
            logger.error(
                "SOCIAL GROUP API VIEW - DELETE: {}".format(vns)
            )
            raise

        except Exception as e:
            logger.error("SOCIAL GROUP API VIEW - DELETE: {}".format(e))
            raise ce.InternalServerError


def retrieve_group(request) -> Response:
    """
    Retrieves details of a social group based on query parameters.

    Returns the group's information or an error message if not found.
    """
    try:
        group_code = request.query_params.get("group_code")
        user_code = request.query_params.get("user_code")

        groups = fetch_groups(
            group_code=group_code, user_code=user_code
        )
        if groups:
            return Response(
                {
                    "message": "Group found successfully",
                    "data": groups,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Group does not exist",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except ce.ValidationFailed as vf:
        logger.error("RETRIEVE GROUP: {}".format(vf))
        raise
    except Exception as e:
        logger.error("RETRIEVE GROUP: {}".format(e))
        raise ce.InternalServerError


def create_group_instance(request) -> Response:
    """
    Creates a new social group using the data provided in the request.

    Returns a success message if the group is created successfully.
    """
    try:
        name = request.data["name"]
        description = request.data["description"]

        group = create_group(name=name, description=description)
        if group:
            return Response(
                {
                    "message": "Group created successfully",
                    "data": {"group_code": group.code},
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "Failed to create group",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except ce.ErrorMSG as em:
        logger.error("CREATE GROUP: {}".format(em))
        raise
    except ce.ValidationFailed as vf:
        logger.error("CREATE GROUP: {}".format(vf))
        raise
    except ce.DuplicateKey as dk:
        logger.error("CREATE GROUP: {}".format(dk))
        raise
    except Exception as e:
        logger.error("CREATE GROUP: {}".format(e))
        raise ce.InternalServerError


def delete_group_instance(group_code) -> Response:
    """
    Deletes a social group identified by its unique code.

    Returns a success message if the deletion is successful.
    """
    try:
        deletion_success = delete_group(group_code=group_code)
        if deletion_success:
            return Response(
                {
                    "message": "Group deleted successfully",
                    "data": None,
                },
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(
            {
                "message": "Group not found or deletion failed",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except ce.ValidationFailed as vf:
        logger.error("DELETE GROUP: {}".format(vf))
        raise
    except Exception as e:
        logger.error("DELETE GROUP: {}".format(e))
        raise ce.InternalServerError


def fetch_groups(
    group_code: uuid.UUID, user_code: uuid.UUID
) -> List[SocialGroup]:
    """
    Fetches all social groups or filters them by group code and user code.

    Returns a list of social groups or an empty list if none are found.
    """
    try:
        groups = session.query(
            SocialGroup.code.label("group_code"),
            SocialGroup.name,
            SocialGroup.description,
        ).filter(SocialGroup.deleted_at.is_(None))

        if group_code:
            groups = groups.filter(SocialGroup.code == group_code)
        if user_code:
            groups = groups.join(
                GroupMembership,
                SocialGroup.id == GroupMembership.group_id,
            ).join(
                User,
                and_(
                    GroupMembership.user_id == User.id,
                    User.code == user_code,
                    GroupMembership.deleted_at.is_(None),
                ),
            )

        groups = groups.all()
        session.commit()

        groups = result_list_to_dict(groups) if groups else None

    except Exception as e:
        logger.error("FETCH GROUPS: {}".format(e))
        session.rollback()
        groups = []

    return groups


def create_group(name: str, description: str) -> Optional[SocialGroup]:
    """
    Creates a new social group in the database.

    Returns the created group object or None if the creation fails.
    """
    try:
        group = SocialGroup(name=name, description=description)
        session.add(group)
        session.commit()
    except alchexc.IntegrityError as ie:
        logger.error("CREATE GROUP: {}".format(ie))
        session.rollback()
        raise ce.ErrorMSG("Duplicate record found for group name")

    except Exception as e:
        logger.error("CREATE GROUP: {}".format(e))
        session.rollback()
        group = None
    return group


def delete_group(group_code: str) -> bool:
    """
    Marks a social group as deleted based on its unique code.

    Returns True if the deletion is successful, otherwise False.
    """
    try:
        group = (
            session.query(SocialGroup)
            .filter(SocialGroup.code == group_code)
            .one_or_none()
        )
        if group:
            group.deleted_at = datetime.now()
            session.commit()
            return True
    except Exception as e:
        logger.error("DELETE GROUP: {}".format(e))
        session.rollback()
    return False
