import pytest
from django.utils import timezone
from django.urls import reverse
from django.contrib.messages import get_messages
from services.models import Listing
from datetime import date, datetime, timedelta


requiresDB = pytest.mark.django_db
params = pytest.mark.parametrize

def valid_post_data(**overrides):
    data = {
        "service_type": "offer",
        "title": "Linear Algebra tutoring",
        "category": "Tutoring",
        "date": (timezone.localdate() + timedelta(days=1)).isoformat(),
    }
    data.update(overrides)
    return data


def make_test_post(author, **kwargs):
    defaults = {
        'service_type': 'offer',
        'title': 'Test Post',
        'description': 'test description',
        'category': 'tutoring',
        'date': date(2027, 12, 1),
    }
    defaults.update(kwargs)
    return Listing.objects.create(author=author, **defaults)


def get_titles(response):
    titles = []
    for i in response.context['page_obj']:
        titles.append(i.title)

    return titles


def set_creation_date(post, year, month, day):
    Listing.objects.filter(pk=post.pk).update(created_at=timezone.make_aware(datetime(year, month, day)))


@requiresDB
def test_new_post_page_shows_form_fields(client, test_user):
    response = client.get(reverse("new_listing"))
    assert response.status_code == 200
    form = response.context["form"]
    assert list(form.fields) == ["service_type", "title", "description", "category", "date"]
    assert response.context["today"] == timezone.localdate().isoformat()


@requiresDB
def test_valid_post_creates_listing_for_current_user(client, test_user):
    response = client.post(reverse("new_listing"), valid_post_data())
    assert response.status_code == 302
    assert response.url == reverse("new_listing")
    listing = Listing.objects.get()
    assert listing.author == test_user
    assert listing.title == "Linear Algebra tutoring"
    assert listing.service_type == "offer"


@requiresDB
def test_valid_post_shows_success_message(client, test_user):
    response = client.post(reverse("new_listing"), valid_post_data())
    messages = [str(i) for i in get_messages(response.wsgi_request)]
    assert len(messages) == 1
    assert "Your listing has been saved!" in messages[0]
    assert "Linear Algebra tutoring" in messages[0]


@requiresDB
def test_past_date_is_rejected(client, test_user):
    yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
    response = client.post(reverse("new_listing"), valid_post_data(date=yesterday))
    assert response.status_code == 200
    assert "Service date cannot be in the past." in response.context["form"].errors["date"]
    assert Listing.objects.count() == 0
    messages = [str(i) for i in get_messages(response.wsgi_request)]
    assert "An error occurred. Please check your entry and try again." in messages


@requiresDB
def test_today_is_accepted(client, test_user):
    today = timezone.localdate().isoformat()
    response = client.post(reverse("new_listing"), valid_post_data(date=today))
    assert response.status_code == 302
    assert Listing.objects.count() == 1


@requiresDB
@params("missing_field", ["service_type", "title", "date"])
def test_required_fields_are_enforced(client, test_user, missing_field):
    data = valid_post_data()
    data.pop(missing_field)
    response = client.post(reverse("new_listing"), data)
    assert response.status_code == 200
    assert missing_field in response.context["form"].errors
    assert Listing.objects.count() == 0


@requiresDB
def test_category_is_optional(client, test_user):
    data = valid_post_data()
    data.pop("category")
    response = client.post(reverse("new_listing"), data)
    assert response.status_code == 302
    assert Listing.objects.count() == 1


@requiresDB
def test_invalid_service_type_is_rejected(client, test_user):
    response = client.post(reverse("new_listing"), valid_post_data(service_type="invalidtype"))
    assert response.status_code == 200
    assert "service_type" in response.context["form"].errors
    assert Listing.objects.count() == 0


# ----------------Filter Tests--------------------
@requiresDB
def test_filter_by_service_type(client, test_user):
    make_test_post(test_user, title='Offer A', service_type='offer')
    make_test_post(test_user, title='Request A', service_type='request')
    response = client.get(reverse('all_listings_view'), {'type': 'offer'})
    assert get_titles(response) == ['Offer A']


@requiresDB
def test_filter_by_category(client, test_user):
    make_test_post(test_user, title='Post A', category='Tutoring')
    make_test_post(test_user, title='Post B', category='General Labor')
    response = client.get(reverse('all_listings_view'), {'category': 'General Labor'})
    assert get_titles(response) == ['Post B']


@requiresDB
def test_filters_combined(client, test_user):
    make_test_post(test_user, title='Matching Post', service_type='request', category='Tutoring')
    make_test_post(test_user, title='Wrong Type', service_type='offer', category='Tutoring')
    make_test_post(test_user, title='Wrong Category', service_type='request', category='General Labor')
    response = client.get(reverse('all_listings_view'), {'type': 'request', 'category': 'Tutoring'})
    assert get_titles(response) == ['Matching Post']


@requiresDB
def test_invalid_type_is_ignored(client, test_user):
    make_test_post(test_user, title='Post A', service_type='offer')
    make_test_post(test_user, title='Post B', service_type='request')
    response = client.get(reverse('all_listings_view'), {'type': 'Not Valid'})
    assert response.status_code == 200
    assert len(get_titles(response)) == 2


@requiresDB
def test_no_matches_returns_empty_page(client, test_user):
    make_test_post(test_user, service_type='offer')
    response = client.get(reverse('all_listings_view'), {'type': 'request'})
    assert response.status_code == 200
    assert get_titles(response) == []


# ------------------Sorting Tests----------------
@requiresDB
def test_default_sort_is_newest_posted_first(client, test_user):
    old_post = make_test_post(test_user, title='Old')
    new_post = make_test_post(test_user, title='New')
    set_creation_date(old_post, 2027, 1, 1)
    set_creation_date(new_post, 2027, 10, 1)
    response = client.get(reverse('all_listings_view'))
    assert get_titles(response) == ['New', 'Old']


@requiresDB
def test_sort_posted_old(client, test_user):
    old_post = make_test_post(test_user, title='Old')
    new_post = make_test_post(test_user, title='New')
    set_creation_date(old_post, 2027, 1, 1)
    set_creation_date(new_post, 2027, 10, 1)
    response = client.get(reverse('all_listings_view'), {'sort': 'posted_old'})
    assert get_titles(response) == ['Old', 'New']


@requiresDB
def test_sort_listing_date_soonest_and_latest(client, test_user):
    make_test_post(test_user, title="Late", date=datetime(2027, 11, 1))
    make_test_post(test_user, title="Soon", date=datetime(2027, 3, 1))
    soon = client.get(reverse("all_listings_view"), {"sort": "service_soon"})
    late = client.get(reverse("all_listings_view"), {"sort": "service_late"})
    assert get_titles(soon) == ["Soon", "Late"]
    assert get_titles(late) == ["Late", "Soon"]


@requiresDB
def test_invalid_sort_falls_back_without_error(client, test_user):
    make_test_post(test_user)
    response = client.get(reverse("all_listings_view"), {"sort": "nonsense"})
    assert response.status_code == 200


# ------------------Edit Listing Tests----------------
@requiresDB
def test_edit_page_prefills_form_for_owner(client, test_user):
    post = make_test_post(test_user, title='Original')
    response = client.get(reverse('edit_listing', args=[post.id]))
    assert response.status_code == 200
    assert response.context['form'].instance == post


@requiresDB
def test_owner_can_edit_listing(client, test_user):
    post = make_test_post(test_user, title='Original', service_type='offer')
    response = client.post(
        reverse('edit_listing', args=[post.id]),
        valid_post_data(title='Updated', service_type='request', category='General Labor'),
    )
    assert response.status_code == 302
    assert response.url == reverse('account_summary')
    post.refresh_from_db()
    assert post.title == 'Updated'
    assert post.service_type == 'request'
    assert post.category == 'General Labor'


@requiresDB
def test_edit_does_not_create_new_listing(client, test_user):
    post = make_test_post(test_user)
    client.post(reverse('edit_listing', args=[post.id]), valid_post_data(title='Updated'))
    assert Listing.objects.count() == 1


@requiresDB
def test_cannot_edit_another_users_listing(client, test_user, django_user_model):
    other = django_user_model.objects.create_user(username='other', password='pw12345!')
    post = make_test_post(other, title='Not Yours')
    url = reverse('edit_listing', args=[post.id])
    assert client.get(url).status_code == 404
    assert client.post(url, valid_post_data(title='Hijacked')).status_code == 404
    post.refresh_from_db()
    assert post.title == 'Not Yours'


@requiresDB
def test_edit_nonexistent_listing_returns_404(client, test_user):
    response = client.get(reverse('edit_listing', args=[99999]))
    assert response.status_code == 404


@requiresDB
def test_edit_requires_login(client, test_user):
    post = make_test_post(test_user)
    client.logout()
    response = client.get(reverse('edit_listing', args=[post.id]))
    assert response.status_code == 302
    assert '/user_login' in response.url


@requiresDB
def test_edit_past_date_is_rejected(client, test_user):
    post = make_test_post(test_user, title='Original')
    yesterday = (timezone.localdate() - timedelta(days=1)).isoformat()
    response = client.post(
        reverse('edit_listing', args=[post.id]),
        valid_post_data(title='Updated', date=yesterday),
    )
    assert response.status_code == 200
    assert 'Service date cannot be in the past.' in response.context['form'].errors['date']
    post.refresh_from_db()
    assert post.title == 'Original'


@requiresDB
@params("missing_field", ["service_type", "title", "date"])
def test_edit_required_fields_are_enforced(client, test_user, missing_field):
    post = make_test_post(test_user, title='Original')
    data = valid_post_data()
    data.pop(missing_field)
    response = client.post(reverse('edit_listing', args=[post.id]), data)
    assert response.status_code == 200
    assert missing_field in response.context['form'].errors
    post.refresh_from_db()
    assert post.title == 'Original'


# ------------------Delete Listing Tests----------------
@requiresDB
def test_owner_can_delete_listing(client, test_user):
    post = make_test_post(test_user)
    response = client.post(reverse('delete_listing', args=[post.id]))
    assert response.status_code == 302
    assert response.url == reverse('account_summary')
    assert Listing.objects.count() == 0


@requiresDB
def test_delete_only_removes_target_listing(client, test_user):
    keep = make_test_post(test_user, title='Keep')
    remove = make_test_post(test_user, title='Remove')
    client.post(reverse('delete_listing', args=[remove.id]))
    assert list(Listing.objects.all()) == [keep]


@requiresDB
def test_delete_rejects_get_requests(client, test_user):
    post = make_test_post(test_user)
    response = client.get(reverse('delete_listing', args=[post.id]))
    assert response.status_code == 405
    assert Listing.objects.count() == 1


@requiresDB
def test_cannot_delete_another_users_listing(client, test_user, django_user_model):
    other = django_user_model.objects.create_user(username='other', password='pw12345!')
    post = make_test_post(other, title='Not Yours')
    response = client.post(reverse('delete_listing', args=[post.id]))
    assert response.status_code == 404
    assert Listing.objects.filter(pk=post.pk).exists()


@requiresDB
def test_delete_nonexistent_listing_returns_404(client, test_user):
    response = client.post(reverse('delete_listing', args=[99999]))
    assert response.status_code == 404


@requiresDB
def test_delete_requires_login(client, test_user):
    post = make_test_post(test_user)
    client.logout()
    response = client.post(reverse('delete_listing', args=[post.id]))
    assert response.status_code == 302
    assert '/user_login' in response.url
    assert Listing.objects.filter(pk=post.pk).exists()