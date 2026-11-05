from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from services.forms import CreateListingForm
from services.models import Listing

from services.forms import CreateListingForm

def all_listings_view(request):
	listings = Listing.objects.all().select_related('author__profile').order_by('-created_at')
	paginator = Paginator(listings, 12)
	page_obj = paginator.get_page(request.GET.get('page'))
	return render(request, 'all_listings_view.html', {'page_obj': page_obj})
def new_listing(request):
	if request.method == 'POST':
		form = CreateListingForm(request.POST)

		if form.is_valid():
			listing = form.save(commit=False)
			listing.author = request.user
			listing.save()
			messages.success(request, 'Your listing has been saved!\n'
							 f'listing Type: {form.cleaned_data["service_type"].capitalize()}\n'
							 f'Title: {form.cleaned_data["title"]}\n'
							 f'Category: {form.cleaned_data["category"]}\n'
							 f'Date: {form.cleaned_data["date"]}\n')

			return redirect(request.path)
		else:
			messages.error(request, 'An error occurred. Please check your entry and try again.')
	else:
		form = CreateListingForm()

	return render(request, 'new_listing.html', {
		'form': form,
		'today': timezone.localdate().isoformat(),
	})