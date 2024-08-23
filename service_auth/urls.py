from django.urls import path
from service_auth.views import Authentication


urlpatterns = [
    path(
        "<str:slug>",
        Authentication.as_view(),
        name="authentication",
    )
]
