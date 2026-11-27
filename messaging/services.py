
from django.db import transaction
from django.core.exceptions import PermissionDenied

from messaging.models import Chat, Message, UnreadChat
from accounts.moderation import users_are_blocked


### Messaging API ###


@transaction.atomic
def create_chat(first_user, second_user):
    """
    Create and return a chat between two users.

    Raises:
        ValueError: If both users are the same.
        PermissionDenied: If either user has blocked the other.
    """
    if first_user.pk == second_user.pk:
        raise ValueError("A chat requires two distinct users.")

    if users_are_blocked(first_user, second_user):
        raise PermissionDenied(
            "Chat cannot be created between blocked users."
        )

    chat = Chat.objects.create()
    chat.users.add(first_user, second_user)

    UnreadChat.objects.bulk_create([
        UnreadChat(user=first_user, chat=chat),
        UnreadChat(user=second_user, chat=chat),
    ])

    return chat


@transaction.atomic
def send_message(chat, sender, body):
    """
    Send a message and mark the chat unread for other participants.

    Raises:
        PermissionDenied: If sender is not a chat participant,
        or if either participant has blocked the other.
    """
    if not chat.users.filter(pk=sender.pk).exists():
        raise PermissionDenied(
            "You are not a participant in this chat."
        )

    for recipient in chat.users.exclude(pk=sender.pk):
        if users_are_blocked(sender, recipient):
            raise PermissionDenied(
                "Messages cannot be sent between blocked users."
            )

    message = Message.objects.create(
        chat=chat,
        sender=sender,
        body=body,
    )

    for recipient in chat.users.exclude(pk=sender.pk):
        UnreadChat.objects.update_or_create(
            user=recipient,
            chat=chat,
            defaults={"latest_message_id": message.pk},
        )

    return message
