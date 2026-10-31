import pytest
from datetime import date
from service_app.models import Service
from accounts_app.models import Profile


@pytest.fixture
def test_user(db, django_user_model, client):
    user = django_user_model.objects.create_user(
        username="deepa@unomaha.edu",
        email="deepa@unomaha.edu",
        password="My-Strong-Test-Password-928!",
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.phone_number = "402-123-4567"
    profile.save()
    client.force_login(user)
    return user

@pytest.fixture
def other_test_user(db, django_user_model, client):
    user = django_user_model.objects.create_user(
        username="parker@unomaha.edu",
        password="My-Other-Test-Password-928!",
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.phone_number = "402-765-4321"
    profile.save()
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