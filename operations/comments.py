import hashlib
import logging
from datetime import datetime
from typing import List, Optional

import jwt
from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.versioning import NamespaceVersioning
from rest_framework.views import APIView

from operations import schemas
from social_network.utils import custom_exceptions as ce
from social_network.utils.custom_validator import CustomValidator
from social_network.utils.data_formatter import (
    result_list_to_dict,
    result_row_to_dict,
)
from users.models import Comment, Post, User, GroupMembership

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


class CommentsAPIView(APIView):
    """
    Handle CRUD operations on Comment data.
    """

    versioning_class = VersioningConfig
    permission_classes = (AllowAny,)

    def get(self, request, post_code):
        """
        Retrieve comments on a post or a specific comment.
        """
        try:
            if request.version == "v1":
                response = retrieve_comment(request, post_code)
                return response
            else:
                raise ce.VersionNotSupported

        except ce.ErrorMSG as em:
            logger.error("COMMENT API VIEW - GET: {}".format(em))
            raise

        except ce.ValidationFailed as vf:
            logger.error("COMMENT API VIEW - GET: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("COMMENT API VIEW - GET: {}".format(vns))
            raise

        except Exception as e:
            logger.error("COMMENT API VIEW - GET: {}".format(e))
            raise ce.InternalServerError

    def post(self, request, post_code):
        """
        Create a new Comment instance.
        """
        try:
            if request.version == "v1":
                is_valid = c_validator.validate(
                    request.data, schemas.COMMENT_POST
                )

                if is_valid:
                    response = create_comment_instance(
                        request, post_code
                    )
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
            logger.error("COMMENT API VIEW - POST: {}".format(em))
            raise

        except ce.ValidationFailed as vf:
            logger.error("COMMENT API VIEW - POST: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("COMMENT API VIEW - POST: {}".format(vns))
            raise

        except ce.DuplicateKey as dk:
            logger.error("COMMENT API VIEW - POST: {}".format(dk))
            raise

        except Exception as e:
            logger.error("COMMENT API VIEW - POST: {}".format(e))
            raise ce.InternalServerError


def retrieve_comment(request, post_code) -> Response:
    """
    Retrieve comments on a post.
    """
    try:
        comments = fetch_all_comments(post_code, request.user["id"])

        if comments:
            return Response(
                {
                    "message": "Comment found successfully",
                    "data": comments,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "message": "Comment does not exist",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    except ce.ErrorMSG as em:
        logger.error("RETRIEVE COMMENT: {}".format(em))
        raise
    except Exception as e:
        logger.error("RETRIEVE COMMENT: {}".format(e))
        raise ce.InternalServerError


def create_comment_instance(request, post_code) -> Response:
    """
    Create a new comment on a post.
    """
    try:
        content = request.data.get("content")
        comment = create_comment(
            post_code=post_code,
            user_id=request.user["id"],
            content=content,
        )
        if comment:
            return Response(
                {
                    "message": "Comment created successfully",
                    "data": {"comment_code": comment.code},
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "Failed to create comment",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except ce.ErrorMSG as em:
        logger.error("CREATE COMMENT: {}".format(em))
        raise
    except ce.ValidationFailed as vf:
        logger.error("CREATE COMMENT: {}".format(vf))
        raise
    except ce.DuplicateKey as dk:
        logger.error("CREATE COMMENT: {}".format(dk))
        raise
    except Exception as e:
        logger.error("CREATE COMMENT: {}".format(e))
        raise ce.InternalServerError


def fetch_all_comments(post_code: str, user_id: int) -> List[Comment]:
    """Fetch all comments for a specific post."""
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

        comments = (
            session.query(
                Comment.code.label("comment_code"),
                User.name,
                Comment.content,
            )
            .join(Post, Post.id == Comment.post_id)
            .join(User, Comment.user_id == User.id)
            .filter(
                Post.code == post_code,
                Post.deleted_at.is_(None),
                Comment.deleted_at.is_(None),
            )
            .all()
        )
        session.commit()

        comments = result_list_to_dict(comments) if comments else None

    except ce.ErrorMSG as em:
        logger.error("FETCH ALL COMMENTS: {}".format(em))
        session.rollback()
        raise
    except Exception as e:
        logger.error("FETCH ALL COMMENTS: {}".format(e))
        session.rollback()
        comments = []

    return comments


def create_comment(
    post_code: str, user_id: int, content: str
) -> Optional[Comment]:
    """Create a new comment on a post."""
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

        comment = Comment(
            user_id=user_id, post_id=post.id, content=content
        )
        session.add(comment)
        session.commit()

    except ce.ErrorMSG as em:
        logger.error("CREATE COMMENT: {}".format(em))
        session.rollback()
        raise

    except Exception as e:
        logger.error("CREATE COMMENT: {}".format(e))
        session.rollback()
        comment = None

    return comment
