from django.urls import path
from users.views import UserAPIView


urlpatterns = [
    path(
        "fetch",
        UserAPIView.as_view(),
        name="get_user",
    ),
    path(
        "create",
        UserAPIView.as_view(),
        name="create_user",
    ),
    path(
        "join/<str:group_code>",
        UserAPIView.as_view(),
        name="join_group",
    ),
]
