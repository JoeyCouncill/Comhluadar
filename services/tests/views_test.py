import pytest
from urllib.parse import parse_qs, urlsplit
from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from services.models import Listing


def valid_post_data(**overrides):
    data = {
        "listing_type": "offer",
        "title": "Linear Algebra tutoring",
        "category": "Tutoring",
        "date": (timezone.localdate() + timedelta(days=1)).isoformat(),
    }
    data.update(overrides)
    return data

@pytest.mark.django_db
def test_new_post_page_shows_form_fields(client, test_user):
    response = client.get(reverse("new_post"))

    assert response.status_code == 200
    form = response.context["form"]
    assert list(form.fields) == ["listing_type", "title", "category", "date"]
    assert response.context["today"] == timezone.localdate().isoformat()


@pytest.mark.django_db
def test_valid_post_creates_listing_for_current_user(client, test_user):
    response = client.post(reverse("new_post"), valid_post_data())

    assert response.status_code == 302
    assert response.url == reverse("new_post")

    listing = Listing.objects.get()
    assert listing.author == test_user
    assert listing.title == "Linear Algebra tutoring"
    assert listing.listing_type == "offer"

@pytest.mark.django_db
def test_valid_post_shows_success_message(client, test_user):
    response = client.post(reverse("new_post"), valid_post_data())

    messages = [str(i) for i in get_messages(response.wsgi_request)]
    assert len(messages) == 1
    assert "Your post has been saved!" in messages[0]
    assert "Linear Algebra tutoring" in messages[0]

@pytest.mark.django_db
def test_past_date_is_rejected(client, test_user):
    yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()

    response = client.post(reverse("new_post"), valid_post_data(date=yesterday))

    assert response.status_code == 200
    assert "Service date cannot be in the past." in response.context["form"].errors["date"]
    assert Listing.objects.count() == 0

    messages = [str(i) for i in get_messages(response.wsgi_request)]
    assert "An error occurred. Please check your entry and try again." in messages

@pytest.mark.django_db
def test_today_is_accepted(client, test_user):
    today = timezone.localdate().isoformat()

    response = client.post(reverse("new_post"), valid_post_data(date=today))

    assert response.status_code == 302
    assert Listing.objects.count() == 1

@pytest.mark.django_db
@pytest.mark.parametrize("missing_field", ["listing_type", "title", "date"])
def test_required_fields_are_enforced(client, test_user, missing_field):
    data = valid_post_data()
    data.pop(missing_field)

    response = client.post(reverse("new_post"), data)

    assert response.status_code == 200
    assert missing_field in response.context["form"].errors
    assert Listing.objects.count() == 0

@pytest.mark.django_db
def test_category_is_optional(client, test_user):
    data = valid_post_data()
    data.pop("category")

    response = client.post(reverse("new_post"), data)

    assert response.status_code == 302
    assert Listing.objects.count() == 1

@pytest.mark.django_db
def test_invalid_listing_type_is_rejected(client, test_user):
    response = client.post(reverse("new_post"), valid_post_data(listing_type="invalidtype"))

    assert response.status_code == 200
    assert "listing_type" in response.context["form"].errors
    assert Listing.objects.count() == 0