from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST, require_safe, require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.urls import reverse
from services.forms import EngagementRoundForm, ReviewForm
from services.engagements import (
    complete_engagement, create_listing_request, 
    decide_request, engagement_review_target, 
    request_for_participant, start_request_chat, 
    reopen_listing_request, submit_engagement_review)


def _redirect_to_request_or_chat(item):
    if item.chat_id:
        return redirect("chat_detail", chat_id=item.chat_id)

    return redirect("engagement_request_detail", listing_id=item.listing_id, request_id=item.pk)


@require_POST
def request_engagement(request, listing_id):
    item = create_listing_request(listing_id, request.user)
    if item is None:
        return redirect("listing_detail", listing_id=listing_id)

    return _redirect_to_request_or_chat(item)


@require_safe
def engagement_request_detail(request, listing_id, request_id):
    item = request_for_participant(listing_id, request_id, request.user)
    if item.chat_id:
        return redirect("chat_detail", chat_id=item.chat_id)

    return render(request, "services/engagement_request_detail.html", {"item": item})


@require_POST
def start_engagement_chat(request, listing_id, request_id):
    item = start_request_chat(listing_id, request_id, request.user)
    return _redirect_to_request_or_chat(item)


@require_POST
def decide_engagement_request(request, listing_id, request_id):
    decision = request.POST.get("decision")
    form = EngagementRoundForm(request.POST)

    if decision not in {"agree", "decline"} or not form.is_valid():
        return HttpResponseBadRequest("Invalid engagement decision.")

    item = decide_request(
        listing_id,
        request_id,
        request.user,
        agree=decision == "agree",
        decision_round=form.cleaned_data["decision_round"],
    )

    return _redirect_to_request_or_chat(item)


@require_POST
def reopen_engagement_request(request, listing_id, request_id):
    form = EngagementRoundForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid engagement round.")

    item = reopen_listing_request(
        listing_id,
        request_id,
        request.user,
        decision_round=form.cleaned_data["decision_round"],
    )

    return _redirect_to_request_or_chat(item)

def _engagements_url():
    return reverse("account_summary", fragment="engagements-pane")


@login_required
@require_POST
def mark_engagement_complete(request, listing_id):
    complete_engagement(listing_id, request.user)
    return redirect(_engagements_url())


@login_required
@require_http_methods(["GET", "POST"])
def write_engagement_review(request, listing_id):
    engagement, reviewed_user = engagement_review_target(listing_id, request.user)
    form = ReviewForm(request.POST if request.method == "POST" else None)

    if request.method == "POST" and form.is_valid():
        try:
            submit_engagement_review(
                listing_id,
                request.user,
                rating=form.cleaned_data["rating"],
                comment=form.cleaned_data["comment"],
            )
        except ValidationError as error:
            form.add_error(None, error.messages)
        else:
            return redirect(_engagements_url())

    return render(request, "services/write_engagement_review.html", {
        "engagement": engagement,
        "reviewed_user": reviewed_user,
        "form": form,
    })