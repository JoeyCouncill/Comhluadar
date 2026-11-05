from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_not_required
from django.db import transaction
from accounts.forms import EditProfileForm

@login_not_required
def front_page(request):
	return render(request, "index.html")

def account_summary(request):
    return render(request, "account_summary.html")

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