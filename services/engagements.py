from django.db import transaction
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from messaging.services import create_chat
from notifications.services import notify
from .models import Engagement, Listing, ListingRequest, Review

def requests_for_participant(user):
    """Returns all requests a given user is part of"""
    return ListingRequest.objects.filter(
        Q(listing__author=user) | Q(requester=user)
    ).select_related("listing__engagement")


## Return single request ##
def request_for_participant(listing_id, request_id, user):
    """Returns a specific request a user is part of"""
    return get_object_or_404(requests_for_participant(user), listing_id=listing_id, pk=request_id)


def lock_listing(listing_id):
    """Lock listing until calling function completes to ensure multiple engagements cannot exist"""
    return get_object_or_404(Listing.objects.select_for_update(), pk=listing_id)


def current_listing_request(listing_id, requester_id):
    """returns users current or previously declined request for a listing"""
    requests = ListingRequest.objects.filter(
        listing_id=listing_id,
        requester_id=requester_id,
    ).order_by("-created_at", "-pk")

    return requests.filter(declined_at__isnull=True).first() or requests.first()


def can_reopen_request(item, user):
    if item.declined_at is None or hasattr(item.listing, "engagement"):
        return False

    if item.declined_by_role == ListingRequest.DeclinedBy.REQUESTER:
        allowed_user_id = item.requester_id
    else:
        allowed_user_id = item.listing.author_id

    if user.pk != allowed_user_id:
        return False

    current = current_listing_request(item.listing_id, item.requester_id)
    return current is not None and current.pk == item.pk


def _notify_request(item, recipient, text):
    """Engagement notification function"""
    notify(
        recipient=recipient,
        text=text,
        url=reverse("engagement_request_detail", kwargs={"listing_id": item.listing_id, "request_id": item.pk}),
    )

    
@transaction.atomic
def create_listing_request(listing_id, user):
    listing = lock_listing(listing_id)
    ### Checks ###
    if listing.author_id == user.pk:
        raise Http404

    existing = current_listing_request(listing_id, user.pk)
    if existing is not None:
        return existing

    if hasattr(listing, "engagement"):
        return None
    ### End Checks ###

    item = ListingRequest.objects.create(listing=listing, requester=user)

    _notify_request(
        item,
        listing.author,
        f'Someone is interested in "{listing.title}". Would you like to start a chat?',
    )
    
    return item


@transaction.atomic
def start_request_chat(listing_id, request_id, user):
    lock_listing(listing_id)
    item = request_for_participant(listing_id, request_id, user)
    if item.listing.author_id != user.pk:
        raise Http404

    if item.chat_id is None and item.is_open:
        item.chat = create_chat(user, item.requester)
        item.save(update_fields=["chat"])

    return item


@transaction.atomic
def reopen_listing_request(listing_id, request_id, user, *, decision_round):
    lock_listing(listing_id)
    item = request_for_participant(listing_id, request_id, user)

    if item.decision_round != decision_round or item.declined_at is None:
        return item

    if not can_reopen_request(item, user):
        raise PermissionDenied

    ### Reset fields ###
    item.declined_at = None
    item.declined_by_role = ""
    item.author_agreed_at = None
    item.requester_agreed_at = None
    item.decision_round += 1
    item.save(update_fields=[
        "declined_at",
        "declined_by_role",
        "author_agreed_at",
        "requester_agreed_at",
        "decision_round",
    ])

    if user.pk == item.listing.author_id:
        other_user = item.requester
    else:
        other_user = item.listing.author

    _notify_request(item, other_user, f'The engagement request for "{item.listing.title}" was reopened.')

    return item


@transaction.atomic
def decide_request(listing_id, request_id, user, *, agree, decision_round=None):
    lock_listing(listing_id)
    item = request_for_participant(listing_id, request_id, user)

    if decision_round is not None and item.decision_round != decision_round:
        return item

    if not item.can_decide:
        return item

    is_author = user.pk == item.listing.author_id

    if not agree:
        item.declined_at = timezone.now()
        item.declined_by_role = (
            ListingRequest.DeclinedBy.AUTHOR
            if is_author
            else ListingRequest.DeclinedBy.REQUESTER
        )
        item.save(update_fields=["declined_at", "declined_by_role"])
        return item

    agreement_field = "author_agreed_at" if is_author else "requester_agreed_at"
    if getattr(item, agreement_field) is None:
        setattr(item, agreement_field, timezone.now())
        item.save(update_fields=[agreement_field])

    if item.author_agreed_at and item.requester_agreed_at:
        Engagement.objects.create(listing_id=listing_id, request=item)

    return item


def engagements_for_participant(user):
    return Engagement.objects.filter(Q(listing__author=user) | Q(request__requester=user))


def engagement_for_participant(listing_id, user):
    return get_object_or_404(
        engagements_for_participant(user)
        .filter(request__isnull=False)
        .select_related("listing__author", "request__requester"),
        listing_id=listing_id,
    )


@transaction.atomic
def complete_engagement(listing_id, user):
    lock_listing(listing_id)
    engagement = engagement_for_participant(listing_id, user)

    if engagement.completed_at is None:
        engagement.completed_at = timezone.now()
        engagement.save(update_fields=["completed_at"])

    return engagement


def engagement_review_target(listing_id, user):
    engagement = engagement_for_participant(listing_id, user)

    if engagement.completed_at is None:
        raise PermissionDenied("Complete the engagement before writing a review.")

    if user.pk == engagement.listing.author_id:
        reviewed_user = engagement.request.requester
    else:
        reviewed_user = engagement.listing.author

    return engagement, reviewed_user


@transaction.atomic
def submit_engagement_review(listing_id, user, *, rating, comment):
    listing = lock_listing(listing_id)
    _, reviewed_user = engagement_review_target(listing_id, user)

    existing_review = Review.objects.filter(listing=listing, reviewer=user, reviewed_user=reviewed_user).first()

    if existing_review is not None:
        return existing_review

    review = Review(
        listing=listing,
        reviewer=user,
        reviewed_user=reviewed_user,
        reviewed_role=listing.review_role_for(reviewed_user.pk),
        rating=rating,
        comment=comment,
    )

    review.full_clean()
    review.save()
    return review