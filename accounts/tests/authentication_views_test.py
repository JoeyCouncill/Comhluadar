import pytest
from urllib.parse import parse_qs, urlsplit
from django.urls import reverse


requiresDB = pytest.mark.django_db
params = pytest.mark.parametrize

@requiresDB
def test_login_page_loads(client):
    response = client.get(reverse("user_login"))
    assert response.status_code == 200
    assert b"Email" in response.content
    assert b"Password" in response.content


@requiresDB
def test_create_account_page_loads(client):
    response = client.get(reverse("create_account"))
    assert response.status_code == 200
    assert b"First Name" in response.content
    assert b"Last Name" in response.content
    assert b"UNO Email" in response.content
    assert b"Confirm Password" in response.content


@requiresDB
def test_login_page_links_to_create_account(client):
    response = client.get(reverse("user_login"))
    create_account_url = reverse("create_account")
    assert create_account_url.encode() in response.content


@requiresDB
def test_create_account_page_links_to_login(client):
    response = client.get(reverse("create_account"))
    login_url = reverse("user_login")
    assert login_url.encode() in response.content


@requiresDB
@params(
    "page",
    ["account_summary", "all_listings_view", "new_listing", "inbox"])
@params("method", ["get", "post"])
def test_protected_pages_redirect_anonymous_users(client, page, method):
    url = reverse(page)
    response = getattr(client, method)(url)
    assert response.status_code == 302
    destination = urlsplit(response.url)
    assert destination.path == reverse("user_login")
    assert parse_qs(destination.query)["next"] == [url]


@requiresDB
@params(
    "page",
    ["account_summary", "all_listings_view", "new_listing", "inbox"])
def test_protected_pages_allow_logged_in_users(client, test_user, page):
    client.force_login(test_user)
    response = client.get(reverse(page))
    assert response.status_code == 200


@requiresDB
def test_login_authenticates_user(client, test_user):
    response = client.post(
        reverse("user_login"),
        {
            "email": test_user.username,
            "password": "My-Strong-Test-Password-928!",
    })
    assert response.status_code == 302
    assert response.url == reverse("account_summary")
    assert int(client.session["_auth_user_id"]) == test_user.pk


@requiresDB
def test_wrong_password_does_not_log_user_in(client, django_user_model):
    django_user_model.objects.create_user(username="student@unomaha.edu", password="My-Strong-Test-Password-928!")    

    response = client.post(
        reverse("user_login"),
        {
            "username": "student@unomaha.edu",
            "password": "wrong-password",
    })
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session

