from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_not_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from accounts_app.models import Profile


User = get_user_model()

def hello_world(request):
	return HttpResponse('Hello world!<br><br>This is the root page for Comhluadar!')

@login_not_required
def front_page(request):
	return render(request, "index.html")

@login_not_required
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("account_summary")

        messages.error(request, "Invalid email, username, or password.")
    
    return render(request, "user_login.html")

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

def account_summary(request):
    return render(request, "account_summary.html")

def edit_profile(request):
    return render(request, "edit_profile.html")