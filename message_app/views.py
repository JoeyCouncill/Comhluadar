from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

def user_inbox(request):
	return render(request, "user_inbox_css.html")