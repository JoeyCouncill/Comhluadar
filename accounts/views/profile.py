from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Avg
from accounts.forms import EditProfileForm
from accounts.models import UserReview
from services.models import *

@login_not_required
def front_page(request):
    return render(request, "index.html")


def account_summary(request):
    reviews = (
        UserReview.objects
        .filter(reviewed_user=request.user)
        .select_related("reviewer")
        .order_by("-created_at")
    )

    average_rating = reviews.aggregate(
        average=Avg("rating")
    )["average"]

    review_count = reviews.count()

    context = {
        "reviews": reviews,
        "average_rating": average_rating,
        "review_count": review_count,
    }

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

def user_profile(request, user_id):
    profile_user = get_object_or_404(get_user_model().objects.select_related('profile'), pk=user_id)
    listings = Listing.objects.filter(author=profile_user).order_by('-created_at')
    return render(request, 'user_profile.html', {
        'profile_user': profile_user,
        'listings': listings,
    })