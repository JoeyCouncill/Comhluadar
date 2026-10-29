from django.conf import settings
from django.db import models


class Chat(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="chats",
    )

    ##allow chats to be tied to specific service offers/requests 
    # (we dont have to use/implement if we dont want just thought it would be nice)
    service = models.ForeignKey(
        "service_app.Service",
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