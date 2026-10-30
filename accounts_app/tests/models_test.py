from django.db import IntegrityError, transaction
import pytest
from accounts_app.models import Profile, UserBlock, UserReview


def test_profile_model_links_to_user(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.phone_number = "402-123-4567"
    profile.save()
    user.refresh_from_db()
    assert user.profile.phone_number == "402-123-4567"


def test_user_cannot_have_two_profiles(user):
    Profile.objects.get_or_create(user=user)
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Profile.objects.create(user=user)


def test_user_cannot_review_self(user):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserReview.objects.create(
                reviewer=user,
                reviewed_user=user,
                rating=5,
            )


def test_user_cannot_review_same_person_twice(user, other_user):
    UserReview.objects.create(
        reviewer=user,
        reviewed_user=other_user,
        rating=4,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserReview.objects.create(
                reviewer=user,
                reviewed_user=other_user,
                rating=5,
            )




@pytest.mark.parametrize("rating", [0, 6])
def test_user_rating_reject_not_between_one_and_five(
    user, other_user, rating
):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserReview.objects.create(
                reviewer=user,
                reviewed_user=other_user,
                rating=rating,
            )


@pytest.mark.parametrize("rating", [1, 5])
def test_user_rating_accept_between_one_and_five(user, other_user, rating):
    review = UserReview.objects.create(
        reviewer=user,
        reviewed_user=other_user,
        rating=rating,
    )
    review.refresh_from_db()
    assert review.rating == rating


def test_user_cannot_block_self(user):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserBlock.objects.create(blocker=user, blocked=user)


def test_duplicate_block_rejected(user, other_user):
    UserBlock.objects.create(blocker=user, blocked=other_user)

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            UserBlock.objects.create(blocker=user, blocked=other_user)


def test_block_is_directional(user, other_user):
    UserBlock.objects.create(blocker=user, blocked=other_user)

    assert user.blocks_created.filter(blocked=other_user).exists()
    assert not other_user.blocks_created.filter(blocked=user).exists()