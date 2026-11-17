
import pytest

from django.urls import reverse
from services.models import Listing, Review


@pytest.fixture
def review_data(test_user, django_user_model):
    """
    Create a listing and two reviews:
    - The provider receives a 5-star review.
    - The recipient receives a 4-star review.
    """
    recipient = django_user_model.objects.create_user(
        username="review_recipient@unomaha.edu",
        email="review_recipient@unomaha.edu",
        password="TestPassword123!",
        first_name="Demo",
        last_name="Recipient",
    )

    listing = Listing.objects.create(
        author=test_user,
        service_type="offer",
        title="Math Tutoring",
        date="2026-11-21",
    )

    provider_review = Review(
        listing=listing,
        reviewer=recipient,
        reviewed_user=test_user,
        reviewed_role="provider",
        rating=5,
        comment="Excellent tutoring!",
    )
    provider_review.full_clean()
    provider_review.save()

    recipient_review = Review(
        listing=listing,
        reviewer=test_user,
        reviewed_user=recipient,
        reviewed_role="recipient",
        rating=4,
        comment="Great communication!",
    )
    recipient_review.full_clean()
    recipient_review.save()

    return {
        "listing": listing,
        "provider": test_user,
        "recipient": recipient,
        "provider_review": provider_review,
        "recipient_review": recipient_review,
    }


@pytest.mark.django_db
def test_profile_displays_provider_reviews(client, review_data):
    response = client.get(reverse("account_summary"))

    assert response.status_code == 200
    assert response.context["review_count"] == 1
    assert response.context["provider_review_count"] == 1
    assert response.context["recipient_review_count"] == 0
    assert response.context["average_rating"] == 5

    content = response.content.decode()

    assert "As Provider (1)" in content
    assert "As Recipient (0)" in content
    assert "Excellent tutoring!" in content
    assert "Math Tutoring" in content


@pytest.mark.django_db
def test_listing_displays_both_reviews(client, review_data):
    listing = review_data["listing"]

    response = client.get(
        reverse("listing_detail", args=[listing.pk])
    )

    assert response.status_code == 200
    assert response.context["review_count"] == 2
    assert response.context["average_rating"] == 4.5

    content = response.content.decode()

    assert "Excellent tutoring!" in content
    assert "Great communication!" in content
    assert "Demo Recipient" in content


@pytest.mark.django_db
def test_listing_without_reviews_shows_empty_state(
    client, listing
):
    response = client.get(
        reverse("listing_detail", args=[listing.pk])
    )

    assert response.status_code == 200
    assert response.context["review_count"] == 0
    assert response.context["average_rating"] is None

    assert b"No reviews yet" in response.content


@pytest.mark.django_db
def test_profile_without_reviews_shows_empty_states(
    client, test_user
):
    response = client.get(reverse("account_summary"))

    assert response.status_code == 200
    assert response.context["review_count"] == 0
    assert response.context["provider_review_count"] == 0
    assert response.context["recipient_review_count"] == 0

    content = response.content.decode()

    assert "No provider reviews yet" in content
    assert "No recipient reviews yet" in content
