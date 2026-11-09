from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
import pytest
from urllib.parse import parse_qs, urlsplit
from django.urls import reverse
from service_app.models import Service
from django.contrib.messages import get_messages
import datetime


def valid_post_data(**overrides):
    data = {
        "listing_type": "offer",
        "title": "Linear Algebra tutoring",
        "category": "Tutoring",
        "date": (timezone.localdate() + timedelta(days=1)).isoformat(),
    }
    data.update(overrides)
    return data

def make_test_post(author, **kwargs):
    defaults = {
        'listing_type': 'offer',
        'title': 'Test Post',
        'description': 'test description',
        'category': 'tutoring',
        'date': datetime.date(2026, 12, 1),
    }
    defaults.update(kwargs)
    return Service.objects.create(author=author, **defaults)

def get_titles(response):
    titles = []
    for i in response.context['page_obj']:
        titles.append(i.title)

    return titles

def set_creation_date(post, year, month, day):
    Service.objects.filter(pk=post.pk).update(
        created_at=datetime.datetime(year, month, day)
    )

@pytest.mark.django_db
def test_new_post_page_shows_form_fields(client, test_user):
    response = client.get(reverse("new_post"))

    assert response.status_code == 200
    form = response.context["form"]
    assert list(form.fields) == ["listing_type", "title", "category", "date"]
    assert response.context["today"] == timezone.localdate().isoformat()


@pytest.mark.django_db
def test_valid_post_creates_service_for_current_user(client, test_user):
    response = client.post(reverse("new_post"), valid_post_data())

    assert response.status_code == 302
    assert response.url == reverse("new_post")

    service = Service.objects.get()
    assert service.author == test_user
    assert service.title == "Linear Algebra tutoring"
    assert service.listing_type == "offer"

@pytest.mark.django_db
def test_valid_post_shows_success_message(client, test_user):
    response = client.post(reverse("new_post"), valid_post_data())

    messages = [str(i) for i in get_messages(response.wsgi_request)]
    assert len(messages) == 1
    assert "Your post has been saved!" in messages[0]
    assert "Linear Algebra tutoring" in messages[0]

@pytest.mark.django_db
def test_past_date_is_rejected(client, test_user):
    yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()

    response = client.post(reverse("new_post"), valid_post_data(date=yesterday))

    assert response.status_code == 200
    assert "Service date cannot be in the past." in response.context["form"].errors["date"]
    assert Service.objects.count() == 0

    messages = [str(i) for i in get_messages(response.wsgi_request)]
    assert "An error occurred. Please check your entry and try again." in messages

@pytest.mark.django_db
def test_today_is_accepted(client, test_user):
    today = timezone.localdate().isoformat()

    response = client.post(reverse("new_post"), valid_post_data(date=today))

    assert response.status_code == 302
    assert Service.objects.count() == 1

@pytest.mark.django_db
@pytest.mark.parametrize("missing_field", ["listing_type", "title", "date"])
def test_required_fields_are_enforced(client, test_user, missing_field):
    data = valid_post_data()
    data.pop(missing_field)

    response = client.post(reverse("new_post"), data)

    assert response.status_code == 200
    assert missing_field in response.context["form"].errors
    assert Service.objects.count() == 0

@pytest.mark.django_db
def test_category_is_optional(client, test_user):
    data = valid_post_data()
    data.pop("category")

    response = client.post(reverse("new_post"), data)

    assert response.status_code == 302
    assert Service.objects.count() == 1

@pytest.mark.django_db
def test_invalid_listing_type_is_rejected(client, test_user):
    response = client.post(reverse("new_post"), valid_post_data(listing_type="invalidtype"))

    assert response.status_code == 200
    assert "listing_type" in response.context["form"].errors
    assert Service.objects.count() == 0


# ----------------Filter Tests--------------------
@pytest.mark.django_db
def test_filter_by_listing_type(client, test_user):
    make_test_post(test_user, title='Offer A', listing_type='offer')
    make_test_post(test_user, title='Request A', listing_type='request')

    response = client.get(reverse('all_posts_view'), {'type': 'offer'})

    assert get_titles(response) == ['Offer A']

@pytest.mark.django_db
def test_filter_by_category(client, test_user):
    make_test_post(test_user, title='Post A', category='Tutoring')
    make_test_post(test_user, title='Post B', category='General Labor')

    response = client.get(reverse('all_posts_view'), {'category': 'General Labor'})

    assert get_titles(response) == ['Post B']

@pytest.mark.django_db
def test_filters_combined(client, test_user):
    make_test_post(test_user, title='Matching Post', listing_type='request', category='Tutoring')
    make_test_post(test_user, title='Wrong Type', listing_type='offer', category='Tutoring')
    make_test_post(test_user, title='Wrong Category', listing_type='request', category='General Labor')

    response = client.get(reverse('all_posts_view'), {'type': 'request', 'category': 'Tutoring'})

    assert get_titles(response) == ['Matching Post']

@pytest.mark.django_db
def test_invalid_type_is_ignored(client, test_user):
    make_test_post(test_user, title='Post A', listing_type='offer')
    make_test_post(test_user, title='Post B', listing_type='request')

    response = client.get(reverse('all_posts_view'), {'type': 'Not Valid'})

    assert response.status_code == 200
    assert len(get_titles(response)) == 2

@pytest.mark.django_db
def test_no_matches_returns_empty_page(client, test_user):
    make_test_post(test_user, listing_type='offer')

    response = client.get(reverse('all_posts_view'), {'type': 'request'})

    assert response.status_code == 200
    assert get_titles(response) == []

# ------------------Sorting Tests----------------
@pytest.mark.django_db
def test_default_sort_is_newest_posted_first(client, test_user):
    old_post = make_test_post(test_user, title='Old')
    new_post = make_test_post(test_user, title='New')
    set_creation_date(old_post, 2026, 1, 1)
    set_creation_date(new_post, 2026, 10, 1)

    response = client.get(reverse('all_posts_view'))

    assert get_titles(response) == ['New', 'Old']

@pytest.mark.django_db
def test_sort_posted_old(client, test_user):
    old_post = make_test_post(test_user, title='Old')
    new_post = make_test_post(test_user, title='New')
    set_creation_date(old_post, 2026, 1, 1)
    set_creation_date(new_post, 2026, 10, 1)

    response = client.get(reverse('all_posts_view'), {'sort': 'posted_old'})

    assert get_titles(response) == ['Old', 'New']

@pytest.mark.django_db
def test_sort_service_date_soonest_and_latest(client, test_user):
    make_test_post(test_user, title="Soon", date=datetime.date(2026, 11, 1))
    make_test_post(test_user, title="Late", date=datetime.date(2027, 3, 1))

    soon = client.get(reverse("all_posts_view"), {"sort": "service_soon"})
    late = client.get(reverse("all_posts_view"), {"sort": "service_late"})

    assert get_titles(soon) == ["Soon", "Late"]
    assert get_titles(late) == ["Late", "Soon"]

@pytest.mark.django_db
def test_invalid_sort_falls_back_without_error(client, test_user):
    make_test_post(test_user)

    response = client.get(reverse("all_posts_view"), {"sort": "nonsense"})

    assert response.status_code == 200