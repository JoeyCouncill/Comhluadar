import pytest
from datetime import date
from services.models import Listing
from accounts.models import Profile

@pytest.fixture
def test_user(db, django_user_model, client):
    user = django_user_model.objects.create_user(
        first_name="Deepa",
        last_name="Pollali",
        username="deepa@unomaha.edu",
        email="deepa@unomaha.edu",
        password="My-Strong-Test-Password-928!",
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.skills = "Tutoring"
    profile.other_skill = ""
    profile.interests = "Programming"
    profile.bio = "Deepas bio."
    profile.save()
    client.force_login(user)
    return user

@pytest.fixture
def other_test_user(db, django_user_model, client):
    user = django_user_model.objects.create_user(
        first_name="Parker",
        last_name="Williams",
        username="parker@unomaha.edu",
        email="parker@unomaha.edu",
        password="My-Other-Test-Password-928!",
    )
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.save()
    client.force_login(user)
    return user

@pytest.fixture(autouse=True)
def temporary_media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path / "media"

@pytest.fixture
def listing(test_user):
    return Listing.objects.create(
        author=test_user,
        service_type="offer",
        title="Tutoring",
        date=date(2026, 11, 1),
    )