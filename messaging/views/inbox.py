from django.db.models import Exists, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST
from messaging.forms import MarkChatSeenForm, MessageForm
from messaging.models import Message, UnreadChat
from messaging.services import send_message


def inbox(request):
    newest_message = (
        Message.objects.filter(chat_id=OuterRef("pk")).order_by("-created_at", "-pk").values("created_at")[:1]
    )
    unread_marker = UnreadChat.objects.filter(user=request.user, chat_id=OuterRef("pk"))

    chats = (
        request.user.chats.prefetch_related("users__profile")
        .annotate(is_unread=Exists(unread_marker), last_activity=Coalesce(Subquery(newest_message), "created_at"))
        .order_by("-is_unread", "-last_activity", "-pk")
    )
    return render(request, "messaging/inbox.html", {"chats": chats})


@require_http_methods(["GET", "POST"])
def chat_detail(request, chat_id):
    chat = get_object_or_404(request.user.chats, pk=chat_id)
    form = MessageForm(request.POST if request.method == "POST" else None)

    if request.method == "POST" and form.is_valid():
        send_message(chat, request.user, form.cleaned_data["body"])
        return redirect("chat_detail", chat_id=chat.pk)

    conversation_messages = list(chat.messages.select_related("sender__profile"))
    seen_through = max((message.pk for message in conversation_messages), default=0)

    return render(request, "messaging/chat_detail.html", {
        "chat": chat,
        "conversation_messages": conversation_messages,
        "seen_through": seen_through,
        "form": form,
        "other_participants": chat.users.exclude(pk=request.user.pk).select_related("profile"),
    })


@require_POST
def mark_chat_seen(request, chat_id):
    chat = get_object_or_404(request.user.chats, pk=chat_id)
    form = MarkChatSeenForm(request.POST)

    if not form.is_valid():
        return HttpResponseBadRequest("Invalid message position.")

    seen_through = form.cleaned_data["seen_through"]
    if seen_through and not chat.messages.filter(pk=seen_through).exists():
        return HttpResponseBadRequest("That message does not belong to this chat.")

    UnreadChat.objects.filter(user=request.user, chat=chat).filter(
        Q(latest_message_id__isnull=True) | Q(latest_message_id__lte=seen_through)).delete()

    return HttpResponse(status=204)