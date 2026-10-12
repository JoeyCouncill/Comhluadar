from django.test import TestCase


import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_loads(client):
    response = client.get(reverse("user_login"))

    assert response.status_code == 200
    assert b"Email or Username" in response.content
    assert b"Password" in response.content


@pytest.mark.django_db
def test_create_account_page_loads(client):
    response = client.get(reverse("create_account"))

    assert response.status_code == 200
    assert b"Full Name" in response.content
    assert b"UNO Email" in response.content
    assert b"Confirm Password" in response.content


@pytest.mark.django_db
def test_login_page_links_to_create_account(client):
    response = client.get(reverse("user_login"))

    create_account_url = reverse("create_account")

    assert create_account_url.encode() in response.content


@pytest.mark.django_db
def test_create_account_page_links_to_login(client):
    response = client.get(reverse("create_account"))

    login_url = reverse("user_login")

    assert login_url.encode() in response.content
