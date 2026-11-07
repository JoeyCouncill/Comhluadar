import re
from urllib.parse import urlsplit

import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db

OLD_PASSWORD = "Original-Test-Password-928!"
NEW_PASSWORD = "Replacement-Test-Password-573!"


@pytest.fixture
def reset_user(django_user_model):
    return django_user_model.objects.create_user(
        username="student@unomaha.edu",
        email="student@unomaha.edu",
        password=OLD_PASSWORD,
    )


def request_reset_link(client, mailoutbox, email):
    response = client.post(reverse("password_reset"), {"email": email})
    assert response.status_code == 302
    assert response.url == reverse("password_reset_done")
    assert len(mailoutbox) == 1
    match = re.search(r"https?://[^\s<>]+", mailoutbox[0].body)
    assert match is not None
    return urlsplit(match.group()).path


def test_password_reset_page_loads(client):
    response = client.get(reverse("password_reset"))
    assert response.status_code == 200
    assert "registration/password_reset_form.html" in [template.name for template in response.templates]


def test_reset_sends_email_to_registered_user(client, reset_user, mailoutbox):
    request_reset_link(client, mailoutbox, reset_user.email)
    assert mailoutbox[0].to == [reset_user.email]


def test_unknown_email_shows_confirmation_without_sending(client, mailoutbox):
    response = client.post(reverse("password_reset"), {"email": "unknown@unomaha.edu"})
    assert response.status_code == 302
    assert response.url == reverse("password_reset_done")
    assert len(mailoutbox) == 0


def test_user_can_reset_password(client, reset_user, mailoutbox):
    link = request_reset_link(client, mailoutbox, reset_user.email)
    response = client.get(link, follow=True)
    assert response.status_code == 200
    assert response.context["validlink"] is True
    form_url = response.redirect_chain[-1][0]
    response = client.post(form_url,{"new_password1": NEW_PASSWORD, "new_password2": NEW_PASSWORD})
    assert response.status_code == 302
    assert response.url == reverse("password_reset_complete")
    reset_user.refresh_from_db()
    assert reset_user.check_password(NEW_PASSWORD)
    assert not reset_user.check_password(OLD_PASSWORD)
    response = client.get(link, follow=True)
    assert response.context["validlink"] is False


def test_different_passwords_fail(client, reset_user, mailoutbox):
    link = request_reset_link(client, mailoutbox, reset_user.email)
    response = client.get(link, follow=True)
    form_url = response.redirect_chain[-1][0]
    response = client.post(form_url,{"new_password1": NEW_PASSWORD, "new_password2": "Different-Test-Password-462!"})
    assert response.status_code == 200
    assert "new_password2" in response.context["form"].errors
    reset_user.refresh_from_db()
    assert reset_user.check_password(OLD_PASSWORD)


def test_invalid_token_shows_invalid_link(client, reset_user):
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    url = reverse("password_reset_confirm", kwargs={
        "uidb64": urlsafe_base64_encode(force_bytes(reset_user.pk)), "token": "invalid-token"
        },
    )
    response = client.get(url)
    assert response.status_code == 200
    assert response.context["validlink"] is False