from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from accounts.forms import EditProfileForm
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
        context['listings'] = request.user.listings.order_by(
        "-created_at")

    return render(
        request,
        "account_summary.html",
        context,
    )


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