from django.urls import path

from social_layer.comments.views import (
    CommentSectionView,
    DeleteCommentView,
    ReplyCommentView,
    like_comment,
)

app_name = "comments"

urlpatterns = [
    path(
        "comments/<int:pk>/",
        CommentSectionView.as_view(),
        name="comment_section",
    ),
    path(
        "reply-comment/<int:pk>/",
        ReplyCommentView.as_view(),
        name="reply_comment",
    ),
    path(
        "del-comment/<int:pk>/",
        DeleteCommentView.as_view(),
        name="delete_comment",
    ),
    path(
        "like-comment/<int:pk>/<slug:didlike>/",
        like_comment,
        name="like_comment",
    ),
]
