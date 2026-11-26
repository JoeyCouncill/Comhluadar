import pytest
from django.urls import reverse
from services.engagements import (complete_engagement, create_listing_request, decide_request, start_request_chat)
from services.models import Engagement, Review


@pytest.fixture
def request_with_chat(listing, test_user, other_test_user):
    item = create_listing_request(listing.pk, other_test_user)
    return start_request_chat(listing.pk, item.pk, test_user)


@pytest.fixture
def confirmed_engagement(request_with_chat, test_user, other_test_user):
    item = request_with_chat
    decide_request(item.listing_id, item.pk, test_user, agree=True)
    decide_request(item.listing_id, item.pk, other_test_user, agree=True)
    return Engagement.objects.get(request=item)


@pytest.mark.django_db
def test_request_listing_notifies_author(client, listing, test_user, other_test_user):
    client.force_login(other_test_user)
    response = client.post(reverse("request_engagement", args=[listing.pk]))

    assert response.status_code == 302
    item = listing.engagement_requests.get(requester=other_test_user)
    notice = test_user.notifications.get()
    assert notice.target_url == reverse("engagement_request_detail", args=[listing.pk, item.pk])


@pytest.mark.django_db
def test_both_users_must_agree_to_confirm(client, request_with_chat, test_user, other_test_user):
    item = request_with_chat
    url = reverse("decide_engagement_request", args=[item.listing_id, item.pk])
    data = {"decision": "agree", "decision_round": item.decision_round}

    client.force_login(test_user)
    assert client.post(url, data).status_code == 302
    assert not Engagement.objects.filter(request=item).exists()

    client.force_login(other_test_user)
    assert client.post(url, data).status_code == 302
    assert Engagement.objects.get(listing_id=item.listing_id).request_id == item.pk


@pytest.mark.django_db
def test_only_decliner_can_reopen(client, request_with_chat, test_user, other_test_user):
    item = request_with_chat
    chat_id = item.chat_id
    decide_request(item.listing_id, item.pk, test_user, agree=False)
    url = reverse("reopen_engagement_request", args=[item.listing_id, item.pk])
    data = {"decision_round": item.decision_round}

    client.force_login(other_test_user)
    assert client.post(url, data).status_code == 403

    client.force_login(test_user)
    assert client.post(url, data).status_code == 302
    item.refresh_from_db()
    assert item.declined_at is None
    assert item.chat_id == chat_id


@pytest.mark.django_db
def test_complete_engagement(client, confirmed_engagement, other_test_user):
    client.force_login(other_test_user)
    response = client.post(reverse("mark_engagement_complete", args=[confirmed_engagement.listing_id]))

    assert response.status_code == 302
    confirmed_engagement.refresh_from_db()
    assert confirmed_engagement.completed_at is not None


@pytest.mark.django_db
def test_review_requires_completed_engagement(client, confirmed_engagement, other_test_user):
    client.force_login(other_test_user)
    url = reverse("write_engagement_review", args=[confirmed_engagement.listing_id])

    assert client.post(url, {"rating": 5, "comment": "Great service"}).status_code == 403
    assert not Review.objects.filter(listing=confirmed_engagement.listing).exists()


@pytest.mark.django_db
def test_can_review_after_completion(client, confirmed_engagement, test_user, other_test_user):
    complete_engagement(confirmed_engagement.listing_id, test_user)
    client.force_login(other_test_user)
    url = reverse("write_engagement_review", args=[confirmed_engagement.listing_id])

    assert client.post(url, {"rating": 5, "comment": "Great service"}).status_code == 302
    review = Review.objects.get(listing=confirmed_engagement.listing)
    assert review.reviewer == other_test_user
    assert review.reviewed_user == test_user
    assert review.reviewed_role == Review.Role.PROVIDER
