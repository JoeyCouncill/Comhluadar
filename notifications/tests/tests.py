import pytest
from django.urls import reverse
from notifications.services import notify


@pytest.mark.django_db
def test_inbox_shows_only_signed_in_user_notifications(client, test_user, other_test_user):
    notice = notify(recipient=test_user, text="Your notification")
    notify(recipient=other_test_user, text="Someone else's notification")
    client.force_login(test_user)
    response = client.get(reverse("notifications:inbox"))

    assert response.status_code == 200
    assert list(response.context["notifications"]) == [notice]


@pytest.mark.django_db
@pytest.mark.parametrize("target_route", ["all_listings_view", None])
def test_open_notification_marked_read(client, test_user, target_route):
    target_url = reverse(target_route) if target_route else ""
    notice = notify(recipient=test_user, text="Test notification", url=target_url)
    response = client.post(reverse("notifications:open", args=[notice.pk]))

    assert response.status_code == 302
    assert response.url == (target_url or reverse("notifications:inbox"))
    notice.refresh_from_db()
    assert notice.read_at is not None