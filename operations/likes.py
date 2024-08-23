import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.versioning import NamespaceVersioning
from rest_framework.views import APIView

from social_network.utils import custom_exceptions as ce
from social_network.utils.custom_validator import CustomValidator
from social_network.utils.data_formatter import result_list_to_dict
from operations import schemas
from operations.models import Like, Post, User, GroupMembership

# Get an instance of logger
logger = logging.getLogger("operations")

# Get an instance of Custom Validator
c_validator = CustomValidator({}, allow_unknown=True)

# Create DB Session
session = settings.DB_SESSION


class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


class LikesAPIView(APIView):
    """
    Handles CRUD operations on Like data.
    """

    versioning_class = VersioningConfig
    permission_classes = (AllowAny,)

    def get(self, request, post_code):
        """
        Retrieve a list of all likes on a post or a specific like.
        """
        try:
            if request.version == "v1":

                response = retrieve_like(request, post_code)
                return response

            else:
                raise ce.VersionNotSupported

        except ce.ErrorMSG as em:
            logger.error("LIKE API VIEW - GET: {}".format(em))
            raise

        except ce.ValidationFailed as vf:
            logger.error("LIKE API VIEW - GET: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("LIKE API VIEW - GET: {}".format(vns))
            raise

        except Exception as e:
            logger.error("LIKE API VIEW - GET: {}".format(e))
            raise ce.InternalServerError

    def post(self, request, post_code):
        """
        Toggle a like on a post.
        """
        try:
            if request.version == "v1":
                response = toggle_like_instance(request, post_code)
                return response
            else:
                raise ce.VersionNotSupported

        except ce.ErrorMSG as em:
            logger.error("LIKE API VIEW - POST: {}".format(em))
            raise

        except ce.ValidationFailed as vf:
            logger.error("LIKE API VIEW - POST: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("LIKE API VIEW - POST: {}".format(vns))
            raise

        except Exception as e:
            logger.error("LIKE API VIEW - POST: {}".format(e))
            raise ce.InternalServerError


def retrieve_like(request, post_code) -> Response:
    """
    Retrieve likes on a specific post.
    """
    try:
        likes = fetch_all_likes(post_code, request.user["id"])
        if likes:
            return Response(
                {
                    "message": "Likes found successfully",
                    "data": likes,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "No likes found for the post",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    except ce.ErrorMSG as em:
        logger.error("RETRIEVE LIKE: {}".format(em))
        raise
    except Exception as e:
        logger.error("RETRIEVE LIKE: {}".format(e))
        raise ce.InternalServerError


def toggle_like_instance(request, post_code) -> Response:
    """
    Toggle a like on a specific post.
    """
    try:
        toggled_like = toggle_like(
            post_code=post_code, user_id=request.user["id"]
        )
        if toggled_like:
            return Response(
                {
                    "message": "Action performed successfully",
                    "data": None,
                },
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response(
            {
                "message": "Like not found or deletion failed",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except ce.ErrorMSG as em:
        logger.error("DELETE LIKE: {}".format(em))
        raise
    except Exception as e:
        logger.error("DELETE LIKE: {}".format(e))
        raise ce.InternalServerError


def fetch_all_likes(post_code: str, user_id: int) -> List[Like]:
    """
    Fetch all likes for a specific post.
    """
    try:
        if not (
            session.query(Post)
            .join(
                GroupMembership,
                Post.group_id == GroupMembership.group_id,
            )
            .filter(
                Post.code == post_code,
                GroupMembership.user_id == user_id,
                Post.deleted_at.is_(None),
                GroupMembership.deleted_at.is_(None),
            )
            .all()
        ):
            raise ce.ErrorMSG("You are not member of this post group")

        likes = (
            session.query(User.name, Post.code.label("post_code"))
            .join(Like, Post.id == Like.post_id)
            .join(User, Like.user_id == User.id)
            .filter(
                Post.code == post_code,
                Post.deleted_at.is_(None),
                Like.deleted_at.is_(None),
            )
            .all()
        )
        session.commit()

        likes = result_list_to_dict(likes) if likes else None

    except ce.ErrorMSG as em:
        logger.error("FETCH ALL LIKES: {}".format(em))
        session.rollback()
        raise
    except Exception as e:
        logger.error("FETCH ALL LIKES: {}".format(e))
        session.rollback()
        likes = []

    return likes


def toggle_like(post_code: str, user_id: int) -> Optional[Like]:
    """
    Toggle like status for a post by a user.
    """
    try:
        post = (
            session.query(Post)
            .join(
                GroupMembership,
                Post.group_id == GroupMembership.group_id,
            )
            .filter(
                Post.code == post_code,
                GroupMembership.user_id == user_id,
                Post.deleted_at.is_(None),
                GroupMembership.deleted_at.is_(None),
            )
            .one_or_none()
        )
        if not post:
            raise ce.ErrorMSG("You are not member of this post group")

        # Check if the user has already liked this post
        existing_like = (
            session.query(Like)
            .filter(Like.post_id == post.id, Like.user_id == user_id)
            .one_or_none()
        )
        if existing_like:
            if existing_like.deleted_at is not None:
                existing_like.deleted_at = None
            else:
                existing_like.deleted_at = datetime.now()

            session.commit()
            return True
        else:
            like = Like(user_id=user_id, post_id=post.id)
            session.add(like)
            session.commit()
            return True

    except ce.ErrorMSG as em:
        logger.error("CREATE LIKE: {}".format(em))
        session.rollback()
        raise

    except Exception as e:
        logger.error("CREATE LIKE: {}".format(e))
        session.rollback()
        return False
