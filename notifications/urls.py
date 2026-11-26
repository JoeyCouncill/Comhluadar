from django.urls import path
from notifications.views.inbox import inbox, open_notification

app_name = "notifications"

urlpatterns = [
    path("", inbox, name="inbox"),
    path("<int:notification_id>/open/", open_notification, name="open"),
]