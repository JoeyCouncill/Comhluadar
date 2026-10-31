import pytest
from datetime import date
from service_app.models import Service


@pytest.fixture
def test_user(db, django_user_model, client):
    user = django_user_model.objects.create_user(
        first_name="deepa",
        last_name="Pollali",
        username="deepa",
        password="My-Strong-Test-Password-928!",
    )
    client.force_login(user)
    return user

@pytest.fixture
def other_test_user(db, django_user_model, client):
    user = django_user_model.objects.create_user(
        first_name="parker",
        last_name="williams",
        username="parker",
        password="My-Other-Test-Password-928!",
    )
    client.force_login(user)
    return user

@pytest.fixture
def service(test_user):
    return Service.objects.create(
        author=test_user,
        listing_type="offer",
        title="Tutoring",
        date=date(2026, 11, 1),
    )