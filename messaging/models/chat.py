from django.conf import settings
from django.db import models


class Chat(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chats",
    )

    listing = models.ForeignKey(
        "services.Listing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.pk}"


class Message(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_messages",
    )

    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [models.Index(fields=["chat", "created_at", "id"])]

    def __str__(self):
        return f"Message {self.pk} in chat {self.chat_id}"

class UnreadChat(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="unread_chat_markers",
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    latest_message_id = models.PositiveBigIntegerField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "chat"], name="unique_unread_marker_per_chat_user")]