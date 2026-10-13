from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

def hello_world(request):
	return HttpResponse('Hello world!<br><br>This is the root page for Comhluadar!')

def front_page(request):
	return render(request, "index.html")

def user_login(request):
    return render(request, "user_login.html")

def create_account(request):
    return render(request, "create_account.html")

def account_summary(request):
    return render(request, "account_summary.html")