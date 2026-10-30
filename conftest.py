import pytest
from datetime import date
from service_app.models import Service



@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="deepa",
        password="My-Strong-Test-Password-928!",
    )

@pytest.fixture
def other_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="parker",
        password="My-Other-Test-Password-928!",
    )

@pytest.fixture
def service(user):
    return Service.objects.create(
        author=user,
        listing_type="offer",
        title="Tutoring",
        date=date(2026, 11, 1),
    )