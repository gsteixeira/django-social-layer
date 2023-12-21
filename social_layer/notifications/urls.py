from django.urls import path

from social_layer.notifications.views import (
    ListNotificationsView,
    admin_send_notification,
)

app_name = "notifications"

urlpatterns = [
    path(
        "notifications/",
        ListNotificationsView.as_view(),
        name="view_notifications",
    ),
    path(
        "notifications/adm-send/<int:pk>/",
        admin_send_notification,
        name="admin_send_notification",
    ),
]
