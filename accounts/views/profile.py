from django.shortcuts import render
from django.contrib.auth.decorators import login_not_required


@login_not_required
def front_page(request):
	return render(request, "index.html")

def account_summary(request):
    return render(request, "account_summary.html")

def edit_profile(request):
    return render(request, "edit_profile.html")