from django.urls import path
from operations.groups import SocialGroupsAPIView
from operations.posts import PostsAPIView
from operations.likes import LikesAPIView
from operations.comments import CommentsAPIView


urlpatterns = [
    path(
        "groups",
        SocialGroupsAPIView.as_view(),
        name="all-groups",
    ),
    path(
        "groups/<str:group_code>",
        SocialGroupsAPIView.as_view(),
        name="single-group",
    ),
    path(
        "groups/<str:group_code>/posts",
        PostsAPIView.as_view(),
        name="all-posts",
    ),
    path(
        "posts/<str:post_code>",
        PostsAPIView.as_view(),
        name="single-post",
    ),
    path(
        "posts/<str:post_code>/comments",
        CommentsAPIView.as_view(),
        name="all-comments",
    ),
    path(
        "posts/<str:post_code>/likes",
        LikesAPIView.as_view(),
        name="all-likes",
    ),
    path(
        "comments/<str:comment_code>",
        CommentsAPIView.as_view(),
        name="single-comment",
    ),
]
