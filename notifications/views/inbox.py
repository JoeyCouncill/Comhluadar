from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from notifications.models import Notification
from notifications.services import is_local_target


def inbox(request):
    unread = request.user.notifications.filter(read_at__isnull=True)
    return render(request, "notifications/inbox.html", {"notifications": unread})


@require_POST
def open_notification(request, notification_id):
    owned = Notification.objects.filter(recipient=request.user)
    notice = get_object_or_404(owned, pk=notification_id)
    owned.filter(pk=notice.pk, read_at__isnull=True).update(read_at=timezone.now())

    if is_local_target(notice.target_url):
        return redirect(notice.target_url)
    return redirect("notifications:inbox")