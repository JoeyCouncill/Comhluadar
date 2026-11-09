from django.shortcuts import render, redirect, get_object_or_404
from .models import Service
from .forms import CreateServiceForm
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.models import User 
from django.db.models import Q

#def all_posts_view(request):
#	posts = Service.objects.all().select_related('author__profile').order_by('-created_at')
#	paginator = Paginator(posts, 12)
#	page_obj = paginator.get_page(request.GET.get('page'))
#	return render(request, 'all_posts_view.html', {'page_obj': page_obj})

def all_posts_view(request):

    query = request.GET.get('search', '').strip()

    # Get all posts by default
    posts = Service.objects.all().select_related(
        'author__profile'
    ).order_by('-created_at')

    # Filter posts when search keyword is entered
    if query:
        posts = posts.filter(
            Q(category__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(listing_type__icontains=query)
        )

    # Apply pagination after filtering
    paginator = Paginator(posts, 12)

    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'all_posts_view.html', {
        'page_obj': page_obj,
        'query': query
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

