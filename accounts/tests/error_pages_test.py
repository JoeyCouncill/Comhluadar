import pytest
from django.contrib.auth.decorators import login_not_required
from django.contrib.messages import get_messages
from django.core.exceptions import BadRequest, PermissionDenied
from django.test import Client
from django.urls import path, reverse


# --- Test-only urlconf: routes that deliberately raise ---

@login_not_required
def raise_400(request):
    raise BadRequest

@login_not_required
def raise_403(request):
    raise PermissionDenied

@login_not_required
def raise_500(request):
    raise Exception("test 500")

urlpatterns = [
    path("raise400/", raise_400),
    path("raise403/", raise_403),
    path("raise500/", raise_500),
]

@pytest.fixture
def error_urls(settings):
    settings.ROOT_URLCONF = __name__

def template_names(response):
    return [t.name for t in response.templates]

@pytest.mark.parametrize(
    "url, status, template",
    [
        ("/raise400/", 400, "400.html"),
        ("/raise403/", 403, "403.html"),
        ("/raise500/", 500, "500.html"),
    ],
)
def test_raised_errors_use_custom_pages(error_urls, url, status, template):
    client = Client(raise_request_exception=False)
    response = client.get(url)
    assert response.status_code == status
    assert template in template_names(response)


# --- Real urlconf from here down ---

def test_404_uses_custom_page(client):
    response = client.get("/this-page-does-not-exist/")
    assert response.status_code == 404
    assert "404.html" in template_names(response)


def test_csrf_failure_uses_custom_page():
    client = Client(enforce_csrf_checks=True)
    response = client.post(
        reverse("user_login"),
        {"email": "a@b.com", "password": "x"},
    )
    assert response.status_code == 403
    assert "403_csrf.html" in template_names(response)

def login_messages(response):
    return [str(m) for m in get_messages(response.wsgi_request)]

def test_login_with_next_shows_session_message(client):
    response = client.get(reverse("user_login") + "?next=/some/page/")
    assert any("session may have expired" in m for m in login_messages(response))

def test_login_without_next_shows_no_message(client):
    response = client.get(reverse("user_login"))
    assert login_messages(response) == []


def test_login_with_unsafe_next_shows_no_message(client):
    response = client.get(reverse("user_login") + "?next=https://evil.com/")
    assert login_messages(response) == []