import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

User = get_user_model()


def test_user_uses_email_as_username():
    assert User.USERNAME_FIELD == "email"


@pytest.mark.django_db
def test_create_user_with_email():
    user = User.objects.create_user(
        email="test@test.com",
        password="TestPassword123!",
    )

    assert user.email == "test@test.com"
    assert user.check_password("TestPassword123!")

"""
@pytest.mark.django_db
def test_user_email_is_unique():
    User.objects.create_user(
        email="test@test.com",
        password="TestPassword123!",
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create_user(
                email="test@test.com",
                password="AnotherPassword123!",
            )"""