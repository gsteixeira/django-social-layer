from django.urls import path

from social_layer.posts.views import (
    DeletePost,
    PostDetailView,
    PostsFeedView,
    PostView,
    like_post,
    more_posts,
)

app_name = "posts"

urlpatterns = [
    # posts
    path("new-post/", PostView.as_view(), name="new_post"),
    path("feed/", PostsFeedView.as_view(), name="posts_feed"),
    path("more-posts/", more_posts, name="more_posts"),
    path(
        "post/<int:pk>/",
        PostDetailView.as_view(),
        name="view_post",
    ),
    path(
        "delete-post/<int:pk>/",
        DeletePost.as_view(),
        name="delete_post",
    ),
    path(
        "like-post/<int:pk>/<slug:didlike>/",
        like_post,
        name="like_post",
    ),
]
