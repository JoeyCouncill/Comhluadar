import pytest
from django.urls import reverse
from messaging.services import create_chat


@pytest.fixture
def chat(test_user, other_test_user):
    return create_chat(test_user, other_test_user)


@pytest.mark.django_db
def test_participant_can_send_message(client, chat, test_user, other_test_user):
    other_test_user.unread_chat_markers.filter(chat=chat).delete()
    client.force_login(test_user)
    response = client.post(reverse("chat_detail", args=[chat.pk]), {"body": "Hello!"})

    assert response.status_code == 302
    message = chat.messages.get()
    assert message.sender == test_user
    assert message.body == "Hello!"
    assert other_test_user.unread_chat_markers.filter(chat=chat).exists()


@pytest.mark.django_db
def test_mark_chat_seen_clears_unread_count(client, chat, other_test_user):
    client.force_login(other_test_user)
    counts_url = reverse("activity_counts")
    assert client.get(counts_url).json()["chats"] == 1
    response = client.post(reverse("mark_chat_seen", args=[chat.pk]), {"seen_through": 0})

    assert response.status_code == 204
    assert client.get(counts_url).json()["chats"] == 0


@pytest.mark.django_db
def test_nonparticipant_cannot_view_chat(client, chat, django_user_model):
    client.force_login(django_user_model.objects.create_user(username="chat-outsider"))
    response = client.get(reverse("chat_detail", args=[chat.pk]))

    assert response.status_code == 404