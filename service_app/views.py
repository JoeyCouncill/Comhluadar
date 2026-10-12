from django.shortcuts import render, redirect, get_object_or_404
from .models import Service
from .forms import ServiceForm

def all_posts_view(request):
	return render(request, 'all_posts_view.html')

def new_post(request):
	return render(request, 'new_post.html')