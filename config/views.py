from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

### views for activity badges in side bar ###


@require_GET
@never_cache
def activity_counts(request):
    user = request.user

    return JsonResponse({
        "notifications": user.notifications.filter(read_at__isnull=True).count(),
        "chats": user.unread_chat_markers.filter(chat__users=user).count(),
    })