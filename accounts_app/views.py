from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()

def hello_world(request):
	return HttpResponse('Hello world!<br><br>This is the root page for Comhluadar!')

def front_page(request):
	return render(request, "index.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )
    if user is not None:
        login(request, user)
        return redirect("account_summary")
    
    return render(request, "user_login.html")

def create_account(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        user = User(username=email, email=email, first_name=name)

        user.set_password(password1)
        user.save()
        
    return render(request, "create_account.html")

def account_summary(request):
    return render(request, "account_summary.html")