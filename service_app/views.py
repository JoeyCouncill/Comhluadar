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
	'service_soon': 'date',
	'service_late': '-date',
}

def all_posts_view(request):
	posts = Service.objects.all().select_related('author__profile')

	listing_type = request.GET.get('type', '')
	category = request.GET.get('category', '')
	sort = request.GET.get('sort', 'posted_new')

	if listing_type in ('offer', 'request'):
		posts = posts.filter(listing_type=listing_type)
	if category:
		posts = posts.filter(category=category)

	posts = posts.order_by(SORT_OPTIONS.get(sort, '-created_at'))

	paginator = Paginator(posts, 12)
	page_obj = paginator.get_page(request.GET.get('page'))
	return render(request, 'all_posts_view.html', {
		'page_obj': page_obj,
		'categories': Service._meta.get_field('category').choices,
	})

def new_post(request):
	if request.method == 'POST':
		form = CreateServiceForm(request.POST)

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
		form = CreateServiceForm()

	return render(request, 'new_post.html', {
		'form': form,
		'today': timezone.localdate().isoformat(),
	})

def post_detail(request, post_id):
	post = get_object_or_404(Service.objects.select_related('author__profile'), pk=post_id)
	return render(request, 'listing_detail.html', {'post': post})