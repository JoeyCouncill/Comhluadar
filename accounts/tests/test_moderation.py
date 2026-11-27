
import pytest
from django.urls import reverse

from accounts.models import UserBlock, UserReport


pytestmark = pytest.mark.django_db


@pytest.fixture
def target_user(django_user_model):
    return django_user_model.objects.create_user(
        username="target@unomaha.edu",
        email="target@unomaha.edu",
        password="TestPassword123!",
    )


def test_user_can_block_another_user(client, test_user, target_user):
    response = client.post(
        reverse("block_user", args=[target_user.pk])
    )

    assert response.status_code == 302
    assert UserBlock.objects.filter(
        blocker=test_user,
        blocked=target_user,
    ).count() == 1


def test_duplicate_block_is_prevented(client, test_user, target_user):
    url = reverse("block_user", args=[target_user.pk])

    client.post(url)
    client.post(url)

    assert UserBlock.objects.filter(
        blocker=test_user,
        blocked=target_user,
    ).count() == 1


def test_user_cannot_block_self(client, test_user):
    response = client.post(
        reverse("block_user", args=[test_user.pk])
    )

    assert response.status_code == 302
    assert UserBlock.objects.count() == 0


def test_user_can_unblock(client, test_user, target_user):
    UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    response = client.post(
        reverse("unblock_user", args=[target_user.pk])
    )

    assert response.status_code == 302
    assert not UserBlock.objects.filter(
        blocker=test_user,
        blocked=target_user,
    ).exists()


def test_user_cannot_remove_another_users_block(
    client, test_user, target_user, django_user_model
):
    third_user = django_user_model.objects.create_user(
        username="third@unomaha.edu",
        password="TestPassword123!",
    )

    UserBlock.objects.create(
        blocker=third_user,
        blocked=target_user,
    )

    client.post(
        reverse("unblock_user", args=[target_user.pk])
    )

    assert UserBlock.objects.filter(
        blocker=third_user,
        blocked=target_user,
    ).exists()


def test_valid_report_is_saved(client, test_user, target_user):
    response = client.post(
        reverse("report_user", args=[target_user.pk]),
        {
            "category": UserReport.Category.SPAM,
            "description": "Repeated unsolicited messages.",
        },
    )

    assert response.status_code == 302
    report = UserReport.objects.get()

    assert report.reporter == test_user
    assert report.reported_user == target_user
    assert report.category == UserReport.Category.SPAM
    assert report.status == UserReport.Status.PENDING


def test_blank_description_is_rejected(client, test_user, target_user):
    response = client.post(
        reverse("report_user", args=[target_user.pk]),
        {
            "category": UserReport.Category.SPAM,
            "description": "   ",
        },
    )

    assert response.status_code == 200
    assert UserReport.objects.count() == 0
    assert "description" in response.context["form"].errors


def test_invalid_category_is_rejected(client, test_user, target_user):
    response = client.post(
        reverse("report_user", args=[target_user.pk]),
        {
            "category": "invalid-category",
            "description": "Example report.",
        },
    )

    assert response.status_code == 200
    assert UserReport.objects.count() == 0


def test_user_cannot_report_self(client, test_user):
    response = client.post(
        reverse("report_user", args=[test_user.pk]),
        {
            "category": UserReport.Category.SPAM,
            "description": "Example report.",
        },
    )

    assert response.status_code == 302
    assert UserReport.objects.count() == 0


def test_reporting_does_not_block(client, test_user, target_user):
    client.post(
        reverse("report_user", args=[target_user.pk]),
        {
            "category": UserReport.Category.HARASSMENT,
            "description": "Example report.",
        },
    )

    assert UserReport.objects.count() == 1
    assert UserBlock.objects.count() == 0


@pytest.mark.parametrize(
    "route,method",
    [
        ("block_user", "post"),
        ("unblock_user", "post"),
        ("report_user", "post"),
    ],
)
def test_anonymous_users_cannot_modify_moderation(
    client, target_user, route, method
):
    client.logout()

    response = getattr(client, method)(
        reverse(route, args=[target_user.pk])
    )

    assert response.status_code == 302
    assert UserBlock.objects.count() == 0
    assert UserReport.objects.count() == 0


@pytest.mark.parametrize("route", ["block_user", "unblock_user"])
def test_block_actions_require_post(
    client, test_user, target_user, route
):
    response = client.get(
        reverse(route, args=[target_user.pk])
    )

    assert response.status_code == 405
    assert UserBlock.objects.count() == 0


def test_report_form_loads(client, test_user, target_user):
    response = client.get(
        reverse("report_user", args=[target_user.pk])
    )

    assert response.status_code == 200
    assert "category" in response.context["form"].fields
    assert "description" in response.context["form"].fields

from django.core.exceptions import PermissionDenied

from messaging.models import Chat, Message
from messaging.services import create_chat, send_message


@pytest.mark.parametrize("block_direction", ["sender", "recipient"])
def test_blocked_users_cannot_create_chat(
    test_user, target_user, block_direction
):
    if block_direction == "sender":
        blocker, blocked = test_user, target_user
    else:
        blocker, blocked = target_user, test_user

    UserBlock.objects.create(
        blocker=blocker,
        blocked=blocked,
    )

    with pytest.raises(PermissionDenied):
        create_chat(test_user, target_user)

    assert Chat.objects.count() == 0


@pytest.mark.parametrize("block_direction", ["sender", "recipient"])
def test_blocked_users_cannot_send_messages(
    test_user, target_user, block_direction
):
    chat = create_chat(test_user, target_user)

    if block_direction == "sender":
        blocker, blocked = test_user, target_user
    else:
        blocker, blocked = target_user, test_user

    UserBlock.objects.create(
        blocker=blocker,
        blocked=blocked,
    )

    with pytest.raises(PermissionDenied):
        send_message(chat, test_user, "This should not send.")

    assert Message.objects.filter(chat=chat).count() == 0


def test_nonparticipant_cannot_send_message(
    test_user, target_user, django_user_model
):
    chat = create_chat(test_user, target_user)

    outsider = django_user_model.objects.create_user(
        username="outsider@unomaha.edu",
        password="TestPassword123!",
    )

    with pytest.raises(PermissionDenied):
        send_message(chat, outsider, "Unauthorized message.")

    assert Message.objects.filter(chat=chat).count() == 0


def test_unblocking_restores_messaging(test_user, target_user):
    chat = create_chat(test_user, target_user)

    block = UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    with pytest.raises(PermissionDenied):
        send_message(chat, test_user, "Blocked message")

    block.delete()

    message = send_message(
        chat,
        test_user,
        "Messaging works again.",
    )

    assert message.body == "Messaging works again."
    assert Message.objects.filter(chat=chat).count() == 1

from services.engagements import (
    create_listing_request,
    start_request_chat,
)
from services.models import ListingRequest


@pytest.mark.parametrize("block_direction", ["author", "requester"])
def test_blocked_users_cannot_request_engagement(
    test_user, target_user, listing, block_direction
):
    blocker, blocked = (
        (test_user, target_user)
        if block_direction == "author"
        else (target_user, test_user)
    )

    UserBlock.objects.create(
        blocker=blocker,
        blocked=blocked,
    )

    with pytest.raises(PermissionDenied):
        create_listing_request(listing.pk, target_user)

    assert not ListingRequest.objects.filter(
        listing=listing,
        requester=target_user,
    ).exists()


def test_block_prevents_starting_existing_engagement_chat(
    test_user, target_user, listing
):
    # Create the engagement request before either user blocks.
    item = create_listing_request(listing.pk, target_user)

    # The listing author blocks the requester.
    UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    with pytest.raises(PermissionDenied):
        start_request_chat(
            listing.pk,
            item.pk,
            test_user,
        )

    item.refresh_from_db()

    assert item.chat_id is None
    assert Chat.objects.count() == 0

from services.engagements import (
    decide_request,
    reopen_listing_request,
)


def test_blocked_users_cannot_agree_to_engagement(
    test_user, target_user, listing
):
    item = create_listing_request(listing.pk, target_user)

    UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    with pytest.raises(PermissionDenied):
        decide_request(
            listing.pk,
            item.pk,
            test_user,
            agree=True,
            decision_round=item.decision_round,
        )

    item.refresh_from_db()
    assert item.author_agreed_at is None
    assert item.requester_agreed_at is None


def test_blocked_users_can_decline_engagement(
    test_user, target_user, listing
):
    item = create_listing_request(listing.pk, target_user)

    UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    decide_request(
        listing.pk,
        item.pk,
        test_user,
        agree=False,
        decision_round=item.decision_round,
    )

    item.refresh_from_db()
    assert item.declined_at is not None


def test_blocked_users_cannot_agree_to_engagement(
    test_user, target_user, listing
):
    # Create request and start chat before blocking.
    item = create_listing_request(listing.pk, target_user)
    item = start_request_chat(listing.pk, item.pk, test_user)

    assert item.chat_id is not None

    UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    with pytest.raises(PermissionDenied):
        decide_request(
            listing.pk,
            item.pk,
            test_user,
            agree=True,
            decision_round=item.decision_round,
        )

    item.refresh_from_db()
    assert item.author_agreed_at is None
    assert item.requester_agreed_at is None


def test_blocked_users_can_decline_engagement(
    test_user, target_user, listing
):
    # Start the chat so the request is eligible for decisions.
    item = create_listing_request(listing.pk, target_user)
    item = start_request_chat(listing.pk, item.pk, test_user)

    assert item.can_decide

    UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    decide_request(
        listing.pk,
        item.pk,
        test_user,
        agree=False,
        decision_round=item.decision_round,
    )

    item.refresh_from_db()
    assert item.declined_at is not None
    assert item.declined_by_role == "author"


def test_blocked_users_cannot_reopen_engagement(
    test_user, target_user, listing
):
    # Create request and chat first.
    item = create_listing_request(listing.pk, target_user)
    item = start_request_chat(listing.pk, item.pk, test_user)

    # Decline the engagement before blocking.
    decide_request(
        listing.pk,
        item.pk,
        test_user,
        agree=False,
        decision_round=item.decision_round,
    )

    item.refresh_from_db()
    assert item.declined_at is not None

    original_round = item.decision_round

    UserBlock.objects.create(
        blocker=test_user,
        blocked=target_user,
    )

    with pytest.raises(PermissionDenied):
        reopen_listing_request(
            listing.pk,
            item.pk,
            test_user,
            decision_round=original_round,
        )

    item.refresh_from_db()
    assert item.declined_at is not None
    assert item.decision_round == original_round
