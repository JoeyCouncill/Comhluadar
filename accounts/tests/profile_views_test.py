import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from accounts.models import Profile
from io import BytesIO
from PIL import Image


params = pytest.mark.parametrize

@pytest.fixture
def pf_data():
    return {
        "first_name": "updatedName",
        "last_name": "newName",
        "skills": "Technology",
        "other_skill": "",
        "interests": "Programming",
        "bio": "Hello world.",
    }


def make_image(name="picture.png"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10), color="blue").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


def test_edit_profile_loads_existing_values(client, test_user):
    response = client.get(reverse("edit_profile"))
    assert response.status_code == 200
    form = response.context["form"]
    assert form["first_name"].value() == test_user.first_name
    assert form["last_name"].value() == test_user.last_name
    assert form["skills"].value() == "Tutoring"
    assert form["interests"].value() == "Programming"
    assert form["bio"].value() == "Deepas bio."


def test_valid_submission_saves_changes(client, test_user, pf_data):
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 302
    assert response.url == reverse("account_summary")
    test_user.refresh_from_db()
    profile = Profile.objects.get(user=test_user)
    assert test_user.first_name == pf_data["first_name"]
    assert test_user.last_name == pf_data["last_name"]
    assert profile.skills == pf_data["skills"]
    assert profile.interests == pf_data["interests"]
    assert profile.bio == pf_data["bio"]


@params(
    ("field", "invalid_value"),
    [
        ("first_name", ""),
        ("last_name", ""),
        ("first_name", "x" * 151),
        ("last_name", "x" * 151),
        ("skills", "invalid-choice"),
        ("interests", "x" * 256),
        ("bio", "x" * 501),
    ])
def test_invalid_submission_does_not_save(client, test_user, pf_data, field, invalid_value):
    pf_data[field] = invalid_value
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 200
    assert field in response.context["form"].errors
    test_user.refresh_from_db()
    profile = Profile.objects.get(user=test_user)
    assert test_user.first_name == "Deepa"
    assert test_user.last_name == "Pollali"
    assert profile.skills == "Tutoring"
    assert profile.interests == "Programming"
    assert profile.bio == "Deepas bio."


def test_invalid_submission_preserves_entered_values(client, test_user, pf_data):
    pf_data["bio"] = "x" * 501
    response = client.post(reverse("edit_profile"), pf_data)
    form = response.context["form"]
    assert form["first_name"].value() == "updatedName"
    assert form["interests"].value() == "Programming"
    assert form["bio"].value() == pf_data["bio"]


def test_optional_fields_can_be_empty(client, test_user, pf_data):
    pf_data.update(skills="", other_skill="", interests="", bio="")
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 302
    profile = Profile.objects.get(user=test_user)
    assert profile.skills == ""
    assert profile.other_skill == ""
    assert profile.interests == ""
    assert profile.bio == ""


def test_other_skill_requires_entry(client, test_user, pf_data):
    pf_data.update(skills="Other", other_skill="")
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 200
    assert "other_skill" in response.context["form"].errors
    assert Profile.objects.get(user=test_user).skills == "Tutoring"


def test_other_skill_entry_saves(client, test_user, pf_data):
    pf_data.update(skills="Other", other_skill="Videography")
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 302
    profile = Profile.objects.get(user=test_user)
    assert profile.skills == "Other"
    assert profile.other_skill == "Videography"


def test_cannot_change_email_or_username(client, test_user, pf_data):
    pf_data.update(email="changed@unomaha.edu", school="University of Nebraska Lincoln")
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 302
    test_user.refresh_from_db()
    assert test_user.email == "deepa@unomaha.edu"


@params("field", ["profile_picture", "cover_photo"])
def test_valid_image_upload_saves(client, test_user, pf_data, field):
    pf_data[field] = make_image()
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 302
    profile = Profile.objects.get(user=test_user)
    image = getattr(profile, field)
    assert image.name
    assert image.storage.exists(image.name)


@params("field", ["profile_picture", "cover_photo"])
def test_fake_image_is_rejected(client, test_user, pf_data, field):
    pf_data[field] = SimpleUploadedFile("fake.jpg", b"This is text, not an image.", content_type="image/jpeg")
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 200
    assert field in response.context["form"].errors
    profile = Profile.objects.get(user=test_user)
    assert not getattr(profile, field)
    test_user.refresh_from_db()
    assert test_user.first_name == "Deepa"


@params("field", ["profile_picture", "cover_photo"])
def test_image_over_five_mb_is_rejected(client, test_user, pf_data, field):
    image = make_image()
    image_bytes = image.read()
    oversized_bytes = image_bytes + b"\0" * (5 * 1024 * 1024)
    pf_data[field] = SimpleUploadedFile("large.png", oversized_bytes, content_type="image/png")
    response = client.post(reverse("edit_profile"), pf_data)
    assert response.status_code == 200
    errors = response.context["form"].errors[field]
    assert "Images must be under 5 MB." in errors
    profile = Profile.objects.get(user=test_user)
    assert not getattr(profile, field)