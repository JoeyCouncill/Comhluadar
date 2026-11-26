from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_not_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from accounts.models import Profile

User = get_user_model()

@login_not_required
def user_login(request):
    next_url = request.POST.get("next") or request.GET.get("next", "")
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = ""

    email = ""
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        user = authenticate(request, username=email, password=request.POST.get("password", ""))

        if user is not None:
            login(request, user)
            return redirect(next_url or "all_listings_view")

        messages.error(request, "Invalid email or password.")

    return render(request, "user_login.html", {"next": next_url, "email": email})


@login_not_required
def create_account(request):
    if request.method == "POST":
        firstName = request.POST.get("firstName", "").strip()
        lastName = request.POST.get("lastName", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        errors = []

        if not firstName:
            errors.append("Please enter your first name.")
        if not lastName:
            errors.append("Please enter your last name.")
        try:
            validate_email(email)
        except ValidationError:
            errors.append("Please enter a valid email address.")

        if User.objects.filter(username__iexact=email).exists():
            errors.append("An account with this email already exists.")
        if password1 != password2:
            errors.append("Passwords do not match.")

        user = User(username=email, email=email, first_name=firstName, last_name=lastName)
        try:
            validate_password(password1, user)
        except ValidationError as exc:
            errors.extend(exc.messages)

        if not errors:
            try:
                with transaction.atomic():
                    user.set_password(password1)
                    user.save()
                    Profile.objects.create(user=user)
            except IntegrityError:
                errors.append("An account with this email already exists.")
            else:
                login(request, user)
                return redirect("account_summary")
        for error in errors:
            messages.error(request, error)

    return render(request, "create_account.html")

