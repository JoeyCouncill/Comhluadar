from django.db import IntegrityError, transaction
import pytest
from accounts_app.models import Profile, UserBlock, UserReview


def test_profile_model_links_to_user(test_user):
    assert test_user.profile.phone_number == "402-123-4567"
    assert test_user.profile.display_name == "deepa"


def test_user_cannot_have_two_profiles(test_user):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Profile.objects.create(user=test_user)


def test_user_cannot_review_self(test_user):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserReview.objects.create(
                reviewer=test_user,
                reviewed_user=test_user,
                rating=5,
            )


def test_user_cannot_review_same_person_twice(test_user, other_test_user):
    UserReview.objects.create(
        reviewer=test_user,
        reviewed_user=other_test_user,
        rating=4,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserReview.objects.create(
                reviewer=test_user,
                reviewed_user=other_test_user,
                rating=5,
            )




@pytest.mark.parametrize("rating", [0, 6])
def test_user_rating_reject_not_between_one_and_five(
    test_user, other_test_user, rating
):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserReview.objects.create(
                reviewer=test_user,
                reviewed_user=other_test_user,
                rating=rating,
            )


@pytest.mark.parametrize("rating", [1, 5])
def test_user_rating_accept_between_one_and_five(test_user, other_test_user, rating):
    review = UserReview.objects.create(
        reviewer=test_user,
        reviewed_user=other_test_user,
        rating=rating,
    )
    review.refresh_from_db()
    assert review.rating == rating


def test_user_cannot_block_self(test_user):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserBlock.objects.create(blocker=test_user, blocked=test_user)


def test_duplicate_block_rejected(test_user, other_test_user):
    UserBlock.objects.create(blocker=test_user, blocked=other_test_user)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserBlock.objects.create(blocker=test_user, blocked=other_test_user)


def test_block_is_directional(test_user, other_test_user):
    UserBlock.objects.create(blocker=test_user, blocked=other_test_user)

    assert test_user.blocks_created.filter(blocked=other_test_user).exists()
    assert not other_test_user.blocks_created.filter(blocked=test_user).exists()