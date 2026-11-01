from django.shortcuts import render, redirect, get_object_or_404
from .models import Service
from .forms import ServiceForm
from django.contrib import messages
from django.utils import timezone

def all_posts_view(request):
	return render(request, 'all_posts_view.html')

def new_post(request):
	if request.method == 'POST':
		form = ServiceForm(request.POST)

		if form.is_valid():
			service = form.save(commit=False)
			service.author = request.user
			service.save()
			messages.success(request, 'Your post has been saved!\n'
							 f'Post Type: {form.cleaned_data["listing_type"].capitalize()}\n'
							 f'Title: {form.cleaned_data["title"]}\n'
							 f'Category: {form.cleaned_data["category"]}\n'
							 f'Date: {form.cleaned_data["date"]}\n')

			return redirect(request.path)
		else:
			messages.error(request, 'An error occurred. Please check your entry and try again.')
	else:
		form = ServiceForm()

	return render(request, 'new_post.html', {
		'form': form,
		'today': timezone.localdate().isoformat(),
	})