from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from services.forms import ListingForm

def all_posts_view(request):
	return render(request, 'all_posts_view.html')

def new_post(request):
	if request.method == 'POST':
		form = ListingForm(request.POST)

		if form.is_valid():
			listing = form.save(commit=False)
			listing.author = request.user
			listing.save()
			messages.success(request, 'Your post has been saved!\n'
							 f'Post Type: {form.cleaned_data["listing_type"].capitalize()}\n'
							 f'Title: {form.cleaned_data["title"]}\n'
							 f'Category: {form.cleaned_data["category"]}\n'
							 f'Date: {form.cleaned_data["date"]}\n')

			return redirect(request.path)
		else:
			messages.error(request, 'An error occurred. Please check your entry and try again.')
	else:
		form = ListingForm()

	return render(request, 'new_post.html', {
		'form': form,
		'today': timezone.localdate().isoformat(),
	})