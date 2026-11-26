from django.db import transaction
from messaging.models import Chat, Message, UnreadChat

### Messaging API ###


@transaction.atomic
def create_chat(first_user, second_user):
    """
    Create and return a chat between two users.
    
    Args:
        first_user (User): One of the two users who will be added to the chat.
        second_user (User): One of the two users who will be added to the chat.

    Returns:
        Chat: New chat with both users as participants.

    Raises:
        ValueError: If both Args refer to the same user.
    """
    if first_user.pk == second_user.pk:
        raise ValueError("A chat requires two distinct users.")

    chat = Chat.objects.create()
    chat.users.add(first_user, second_user)
    UnreadChat.objects.bulk_create([UnreadChat(user=first_user, chat=chat), UnreadChat(user=second_user, chat=chat)])
    return chat


@transaction.atomic
def send_message(chat, sender, body):
    """
    Send a message and mark the chat unread for the other participant.

    Args:
        chat (Chat): The chat that will receive the message.
        sender (User): The user sending the message. The function calling send_message must verify
        that this user belongs to the chat.
        body (str): The text of the message.

    Returns:
        Message: The newly saved message.
    """
    message = Message.objects.create(chat=chat, sender=sender, body=body)

    for recipient in chat.users.exclude(pk=sender.pk):
        UnreadChat.objects.update_or_create(user=recipient, chat=chat, defaults={"latest_message_id": message.pk})

    return message