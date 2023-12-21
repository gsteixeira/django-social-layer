from django.urls import path

from social_layer.profiles.views import (
    DeleteProfilePictureView,
    ListProfilesView,
    ProfileView,
    SetupProfileView,
)

app_name = "profiles"

urlpatterns = [
    path(
        "profile/",
        SetupProfileView.as_view(),
        name="setup_profile",
    ),
    path(
        "profile/<int:pk>/",
        ProfileView.as_view(),
        name="view_profile",
    ),
    path(
        "community/",
        ListProfilesView.as_view(),
        name="list_profiles",
    ),
    path(
        "delete-profile-pic/",
        DeleteProfilePictureView.as_view(),
        name="delete_profile_photo",
    ),
]
