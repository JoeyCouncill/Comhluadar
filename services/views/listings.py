from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from services.forms import CreateListingForm
from services.models import Listing
from django.db.models import Q

SORT_OPTIONS = {
	'posted_new': '-created_at',
	'posted_old': 'created_at',
	'listing_soon': 'date',
	'listing_late': '-date',
}

def all_listings_view(request):
	query = request.GET.get('search', '').strip()
	service_type = request.GET.get('type', '')
	category = request.GET.get('category', '')
	sort = request.GET.get('sort', 'posted_new')

	# Get all posts by default

	posts = Listing.objects.all().select_related(
		'author__profile'
	).order_by('-created_at')

	# Filter posts when search keyword is entered
	if query:
		posts = posts.filter(
			Q(category__icontains=query) |
			Q(title__icontains=query) |
			Q(description__icontains=query) |
			Q(service_type__icontains=query)
		)

	# Dropdown Filters
	if service_type in ('offer', 'request'):
		posts = posts.filter(service_type = service_type)
	if category:
		posts = posts.filter(category = category)

	# Sorting
	posts = posts.order_by(SORT_OPTIONS.get(sort, '-created_at'))

	# Apply pagination after filtering
	paginator = Paginator(posts, 12)

	page_obj = paginator.get_page(request.GET.get('page'))

	return render(request, 'all_listings_view.html', {
		'page_obj': page_obj,
		'query': query,
		'categories': Listing._meta.get_field('category').choices,

	})

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

def listing_detail(request, post_id):
	post = get_object_or_404(Listing.objects.select_related('author__profile'), pk=post_id)
	return render(request, 'listing_detail.html', {'post': post})