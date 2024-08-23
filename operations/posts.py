import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union
import uuid
from sqlalchemy import func

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
from operations import schemas
from operations.models import (
    Post,
    SocialGroup,
    User,
    Comment,
    Like,
    GroupMembership,
)

logger = logging.getLogger("operations")
c_validator = CustomValidator({}, allow_unknown=True)

session = settings.DB_SESSION


class VersioningConfig(NamespaceVersioning):
    default_version = "v1"
    allowed_versions = ["v1"]
    version_param = "version"


class PostsAPIView(APIView):
    """
    Handles CRUD operations on Post data.
    """

    versioning_class = VersioningConfig
    permission_classes = (AllowAny,)

    def get(self, request, group_code):
        """
        Retrieve posts in a group or a specific post.
        """
        try:
            if request.version == "v1":
                is_valid = c_validator.validate(
                    request.query_params, schemas.POSTS_GET
                )

                if is_valid:
                    return retrieve_post(request, group_code)
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
            logger.error("POSTS API VIEW - GET: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("POSTS API VIEW - GET: {}".format(vns))
            raise

        except Exception as e:
            logger.error("POSTS API VIEW - GET: {}".format(e))
            raise ce.InternalServerError

    def post(self, request, group_code):
        """
        Create a new Post.
        """
        try:
            if request.version == "v1":
                is_valid = c_validator.validate(
                    request.data, schemas.POSTS_POST
                )

                if is_valid:
                    return create_post_instance(request, group_code)
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
            logger.error("POSTS API VIEW - POST: {}".format(em))
            raise
        except ce.ValidationFailed as vf:
            logger.error("POSTS API VIEW - POST: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("POSTS API VIEW - POST: {}".format(vns))
            raise

        except ce.DuplicateKey as dk:
            logger.error("POSTS API VIEW - POST: {}".format(dk))
            raise

        except Exception as e:
            logger.error("POSTS API VIEW - POST: {}".format(e))
            raise ce.InternalServerError

    def delete(self, request, post_code):
        """
        Delete a Post by its code.
        """
        try:
            if request.version == "v1":
                return delete_post_instance(post_code)
            else:
                raise ce.VersionNotSupported

        except ce.ValidationFailed as vf:
            logger.error("POSTS API VIEW - DELETE: {}".format(vf))
            raise

        except ce.VersionNotSupported as vns:
            logger.error("POSTS API VIEW - DELETE: {}".format(vns))
            raise

        except Exception as e:
            logger.error("POSTS API VIEW - DELETE: {}".format(e))
            raise ce.InternalServerError


def retrieve_post(request, group_code) -> Response:
    """
    Retrieve post data based on the request.
    """
    try:
        post_code = request.query_params.get("post_code")
        posts = fetch_all_posts(
            group_code=group_code, post_code=post_code
        )
        if posts:
            return Response(
                {
                    "message": "Post found successfully",
                    "data": posts,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Post does not exist",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except ce.ValidationFailed as vf:
        logger.error("RETRIEVE POST: {}".format(vf))
        raise
    except Exception as e:
        logger.error("RETRIEVE POST: {}".format(e))
        raise ce.InternalServerError


def create_post_instance(request, group_code) -> Response:
    """
    Create a new Post instance.
    """
    try:
        content = request.data.get("content")
        post = create_post(
            group_code=group_code,
            content=content,
            user_id=request.user["id"],
        )
        if post:
            return Response(
                {
                    "message": "Post created successfully",
                    "data": {"post_code": post.code},
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "message": "Failed to create post",
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except ce.ErrorMSG as em:
        logger.error("CREATE POST INSTANCE: {}".format(em))
        raise
    except ce.ValidationFailed as vf:
        logger.error("CREATE POST INSTANCE: {}".format(vf))
        raise
    except ce.DuplicateKey as dk:
        logger.error("CREATE POST INSTANCE: {}".format(dk))
        raise
    except Exception as e:
        logger.error("CREATE POST INSTANCE: {}".format(e))
        raise ce.InternalServerError


def delete_post_instance(post_code) -> Response:
    """
    Delete a Post by its code.
    """
    try:
        success = delete_post(post_code)
        if success:
            return Response(
                {
                    "message": "Post deleted successfully",
                    "data": None,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "message": "Post does not exist",
                "data": None,
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    except ce.ValidationFailed as vf:
        logger.error("DELETE POST: {}".format(vf))
        raise
    except Exception as e:
        logger.error("DELETE POST: {}".format(e))
        raise ce.InternalServerError


def fetch_all_posts(
    group_code: uuid.UUID, post_code: uuid.UUID = None
) -> List[Post]:
    """
    Fetch posts from a group.
    """
    try:
        comments = (
            session.query(
                Comment.post_id,
                func.count(Comment.post_id).label("total_comments"),
            )
            .filter(Comment.deleted_at.is_(None))
            .group_by(Comment.post_id)
        ).subquery()

        likes = (
            session.query(
                Like.post_id,
                func.count(Like.post_id).label("total_likes"),
            )
            .filter(Like.deleted_at.is_(None))
            .group_by(Like.post_id)
        ).subquery()

        posts = (
            session.query(
                User.name,
                Post.code.label("post_code"),
                Post.content,
                comments.c.total_comments,
                likes.c.total_likes,
            )
            .join(SocialGroup, SocialGroup.id == Post.group_id)
            .join(User, Post.user_id == User.id)
            .outerjoin(comments, Post.id == comments.c.post_id)
            .outerjoin(likes, Post.id == likes.c.post_id)
            .filter(
                SocialGroup.code == group_code,
                SocialGroup.deleted_at.is_(None),
                Post.deleted_at.is_(None),
            )
        )

        if post_code:
            posts = posts.filter(Post.code == post_code)

        posts = posts.all()

        session.commit()

        posts = result_list_to_dict(posts) if posts else None

    except Exception as e:
        logger.error("FETCH ALL POSTS: {}".format(e))
        session.rollback()
        posts = []

    return posts


def create_post(
    group_code: str, user_id: int, content: str
) -> Optional[Post]:
    """
    Create a post in the specified group.
    """
    try:
        group = (
            session.query(SocialGroup)
            .filter(SocialGroup.code == group_code)
            .one_or_none()
        )
        if not group:
            raise ce.ErrorMSG("Group does not exist")
        if not (
            session.query(GroupMembership)
            .filter(
                GroupMembership.user_id == user_id,
                GroupMembership.group_id == group.id,
                GroupMembership.deleted_at.is_(None),
            )
            .first()
        ):
            raise ce.ErrorMSG("Not a member of group")

        post = Post(user_id=user_id, group_id=group.id, content=content)
        session.add(post)
        session.commit()

    except ce.ErrorMSG as em:
        logger.error("CREATE POST: {}".format(em))
        session.rollback()
        raise
    except Exception as e:
        logger.error("CREATE POST: {}".format(e))
        session.rollback()
        post = None
    return post


def delete_post(post_code: str) -> bool:
    """
    Mark a post as deleted.
    """
    try:
        post = (
            session.query(Post)
            .filter(Post.code == post_code)
            .one_or_none()
        )
        if post:
            post.deleted_at = datetime.now()
            session.commit()
            return True
    except Exception as e:
        logger.error("DELETE POST: {}".format(e))
        session.rollback()
    return False
