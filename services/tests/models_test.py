import pytest
from django.core.exceptions import ValidationError
from services.models import Listing, Review


params = pytest.mark.parametrize

@pytest.fixture
def review_data(listing, other_test_user):
    # The existing listing fixture is an offer.
    return {
        "listing": listing,
        "reviewer": other_test_user,
        "reviewed_user": listing.author,
        "reviewed_role": Review.Role.PROVIDER,
        "rating": 4,
        "comment": "",
    }


@params(
    ("service_type", "reviewing_author", "expected_role"),
    [
        ("offer", True, "provider"),
        ("offer", False, "recipient"),
        ("request", True, "recipient"),
        ("request", False, "provider"),
    ])
def test_role_mapping_and_valid_review(listing, other_test_user, service_type, reviewing_author, expected_role):
    listing.service_type = service_type
    listing.save(update_fields=["service_type"])

    if reviewing_author:
        reviewer = other_test_user
        reviewed_user = listing.author
    else:
        reviewer = listing.author
        reviewed_user = other_test_user

    assert listing.review_role_for(reviewed_user.pk) == expected_role
    review = Review(
        listing=listing,
        reviewer=reviewer,
        reviewed_user=reviewed_user,
        reviewed_role=expected_role,
        rating=4,
    )

    review.full_clean()
    review.save()
    review.refresh_from_db()
    assert review.reviewed_role == expected_role


@params(
    ("service_type", "reviewing_author", "wrong_role"),
    [
        ("offer", True, "recipient"),
        ("offer", False, "provider"),
        ("request", True, "provider"),
        ("request", False, "recipient"),
    ])
def test_wrong_role_rejected(listing, other_test_user, service_type, reviewing_author, wrong_role):
    listing.service_type = service_type
    listing.save(update_fields=["service_type"])
    review = Review(
        listing=listing,
        reviewer=(other_test_user if reviewing_author else listing.author),
        reviewed_user=(listing.author if reviewing_author else other_test_user),
        reviewed_role=wrong_role,
        rating=4,
    )

    with pytest.raises(ValidationError) as error:
        review.full_clean()

    assert "reviewed_role" in error.value.message_dict


def test_review_requires_listing_author(review_data, django_user_model):
    third_user = django_user_model.objects.create_user(
        username="third@example.com",
        email="third@example.com",
        password="Third-Test-Password-928!",
    )

    # Neither person is the listing author.
    review_data["reviewed_user"] = third_user

    with pytest.raises(ValidationError, match="One person in this review must be the listing author"):
        Review(**review_data).full_clean()


@params(
    ("changes", "expected_message"),
    [
        ({"rating": 0}, "rating"),
        ({"rating": 6}, "rating"),
        ({"reviewed_role": "unknown"}, "reviewed_role"),
    ])
def test_invalid_values_fail_validation(review_data, changes, expected_message):
    review_data.update(changes)

    with pytest.raises(ValidationError) as error:
        Review(**review_data).full_clean()

    assert expected_message in error.value.message_dict


def test_self_review_fails_validation(review_data):
    review_data["reviewer"] = review_data["reviewed_user"]

    with pytest.raises(ValidationError, match="You cannot review yourself"):
        Review(**review_data).full_clean()


def test_invalid_listing_type_fails_validation(review_data):
    listing = review_data["listing"]
    listing.service_type = "invalid"
    listing.save(update_fields=["service_type"])

    with pytest.raises(ValidationError, match="The listing has an invalid service type"):
        Review(**review_data).full_clean()


def test_duplicate_review_is_rejected(review_data):
    Review.objects.create(**review_data)

    with pytest.raises(ValidationError):
        Review(**review_data).full_clean()


@params("rating", [1, 5])
def test_ratings_1_through_5_allowed(review_data, rating):
    review_data["rating"] = rating
    review = Review(**review_data)
    review.full_clean()
    review.save()
    review.refresh_from_db()
    assert review.rating == rating


def test_engaged_users_can_review_each_other(review_data):
    first_review = Review(**review_data)
    first_review.full_clean()
    first_review.save()

    reverse_review = Review(
        listing=first_review.listing,
        reviewer=first_review.reviewed_user,
        reviewed_user=first_review.reviewer,
        reviewed_role=Review.Role.RECIPIENT,
        rating=5,
    )
    reverse_review.full_clean()
    reverse_review.save()
    assert first_review.listing.reviews.count() == 2
 

def test_review_reverse_relationships(review_data):
    review = Review.objects.create(**review_data)

    assert list(review.listing.reviews.all()) == [review]
    assert list(review.reviewer.reviews_written.all()) == [review]
    assert list(review.reviewed_user.reviews_received.all()) == [review]


def test_role_helper_rejects_invalid_listing_type(listing):
    listing.service_type = "invalid"

    with pytest.raises(ValidationError, match="The listing has an invalid service type"):
        listing.review_role_for(listing.author_id)