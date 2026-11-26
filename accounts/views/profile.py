from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg, Exists, OuterRef, Q
from accounts.forms import EditProfileForm
from services.engagements import engagements_for_participant, requests_for_participant
from services.models import Review


@login_not_required
def front_page(request):
    return render(request, "index.html")


def account_summary(request, user_id=None):
    profile_user = get_object_or_404(User, pk=user_id) if user_id else request.user

    is_own_profile = profile_user == request.user

    reviews = (
        Review.objects
        .filter(reviewed_user=profile_user)
        .select_related("reviewer", "listing")
        .order_by("-created_at")
    )

    # Separate reviews by the role of the person being reviewed.
    provider_reviews = reviews.filter(
        reviewed_role=Review.Role.PROVIDER
    )

    recipient_reviews = reviews.filter(
        reviewed_role=Review.Role.RECIPIENT
    )

    # Overall rating includes both reviews.
    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    context = {
        "reviews": reviews,
        "provider_reviews": provider_reviews,
        "recipient_reviews": recipient_reviews,
        "average_rating": average_rating,
        "review_count": reviews.count(),
        "provider_review_count": provider_reviews.count(),
        "recipient_review_count": recipient_reviews.count(),
        "profile_user": profile_user,
        "is_own_profile": is_own_profile,
    }

    if is_own_profile:
        context["listings"] = (request.user.listings.filter(engagement__isnull=True).order_by("-created_at"))

        reviews_for_this_engagement = Review.objects.filter(listing_id=OuterRef("listing_id"), reviewer=request.user
        ).filter(
                Q(reviewed_user_id=OuterRef("listing__author_id"))
                | Q(reviewed_user_id=OuterRef("request__requester_id"))
        )

        context["confirmed_engagements"] = (
            engagements_for_participant(request.user)
            .select_related("listing__author__profile", "request__requester__profile")
            .annotate(has_reviewed=Exists(reviews_for_this_engagement))
            .order_by("-confirmed_at", "-pk")
        )

        context["pending_requests"] = (
            requests_for_participant(request.user)
            .filter(declined_at__isnull=True, listing__engagement__isnull=True)
            .select_related("listing__author__profile", "requester__profile")
            .order_by("-created_at", "-pk")
        )

    return render(request, "account_summary.html", context)


def edit_profile(request):
    User = request.user

    form = EditProfileForm(
        request.POST if request.method == "POST" else None,
        request.FILES if request.method == "POST" else None,
        instance=User.profile,
        user=User,
    )

    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            User.first_name = form.cleaned_data["first_name"]
            User.last_name = form.cleaned_data["last_name"]
            User.save(update_fields=["first_name", "last_name"])
            form.save()

        return redirect("account_summary")

    return render(request, "edit_profile.html", {"form": form})