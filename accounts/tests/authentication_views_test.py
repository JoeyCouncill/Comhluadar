import pytest
from urllib.parse import parse_qs, urlsplit
from django.urls import reverse

@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get(reverse("login"))
    assert response.status_code == 200
    assert b"Email" in response.content
    assert b"Password" in response.content


@pytest.mark.django_db
def test_signup_page_loads(client):
    response = client.get(reverse("signup"))
    assert response.status_code == 200
    assert b"First Name" in response.content
    assert b"Last Name" in response.content
    assert b"UNO Email" in response.content
    assert b"Confirm Password" in response.content


@pytest.mark.django_db
def test_login_page_links_to_signup(client):
    response = client.get(reverse("login"))
    signup_url = reverse("signup")
    assert signup_url.encode() in response.content


@pytest.mark.django_db
def test_signup_page_links_to_login(client):
    response = client.get(reverse("signup"))
    login_url = reverse("login")
    assert login_url.encode() in response.content

@pytest.mark.django_db
@pytest.mark.parametrize(
    "page",
    ["account_summary", "all_listings_view", "new_listing", "inbox"],
)


@pytest.mark.parametrize("method", ["get", "post"])
def test_protected_pages_redirect_anonymous_users(client, page, method):
    url = reverse(page)
    response = getattr(client, method)(url)
    assert response.status_code == 302
    destination = urlsplit(response.url)
    assert destination.path == reverse("login")
    assert parse_qs(destination.query)["next"] == [url]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "page",
    ["account_summary", "all_listings_view", "new_listing", "inbox"],
)
def test_protected_pages_allow_logged_in_users(
    client, django_user_model, page
):
    user = django_user_model.objects.create_user(
        username="student@unomaha.edu",
        password="Strong-test-password-928!",
    )
    client.force_login(user)
    response = client.get(reverse(page))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_authenticates_user(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="student@unomaha.edu",
        password="My-Strong-Test-Password-928!",
    )
    response = client.post(
        reverse("login"),
        {
            "email": user.username,
            "password": "My-Strong-Test-Password-928!",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("account_summary")
    assert int(client.session["_auth_user_id"]) == user.pk


@pytest.mark.django_db
def test_wrong_password_does_not_log_user_in(client, django_user_model):
    django_user_model.objects.create_user(
        username="student@unomaha.edu",
        password="My-Strong-Test-Password-928!",
    )
    response = client.post(
        reverse("login"),
        {
            "username": "student@unomaha.edu",
            "password": "wrong-password",
        },
    )
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session

