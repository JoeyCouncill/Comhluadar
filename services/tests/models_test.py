import pytest
from django.db import IntegrityError, transaction
from services.models import ServiceReview

pytestmark = pytest.mark.django_db


def test_user_cannot_review_listing_twice(listing, other_test_user):
    ServiceReview.objects.create(
        listing=listing,
        reviewer=other_test_user,
        rating=4,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ServiceReview.objects.create(
                listing=listing,
                reviewer=other_test_user,
                rating=5,
            )


@pytest.mark.parametrize("rating", [0, 6])
def test_listing_rating_reject_not_between_one_and_five(
    listing, other_test_user, rating
):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ServiceReview.objects.create(
                listing=listing,
                reviewer=other_test_user,
                rating=rating,
            )