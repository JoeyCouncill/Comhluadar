from contextlib import nullcontext
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Q
from django.db.models import Avg
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from services.forms import CreateListingForm
from services.models import Listing
from services.engagements import current_listing_request

SORT_OPTIONS = {
    'posted_new': '-created_at',
    'posted_old': 'created_at',
    'service_soon': 'date',
    'service_late': '-date',
}


def all_listings_view(request):
	
    query = request.GET.get('search', '').strip()[:200]
    service_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'posted_new')

    # Get all non engaged posts by default
    posts = (Listing.objects.filter(engagement__isnull=True).select_related("author__profile").order_by("-created_at"))

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
    
    return render(request, 'new_listing.html', {'form': form, 'today': timezone.localdate().isoformat()})


def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing.objects.select_related("author__profile", "engagement"), pk=listing_id)

    reviews = (
        listing.reviews
        .filter(reviewed_user_id=listing.author_id)
        .select_related("reviewer", "reviewed_user")
        .order_by("-created_at")
    )
    
    average_rating = reviews.aggregate(average=Avg("rating"))["average"]

    context = {
        "listing": listing,
        "reviews": reviews,
        "review_count": reviews.count(),
        "average_rating": average_rating,
        "listing_engaged": hasattr(listing, "engagement"),
    }

    if request.user.pk == listing.author_id:
        context["listing_requests"] = (
            listing.engagement_requests
            .select_related("requester__profile", "listing__engagement")
            .order_by("-created_at", "-pk")
        )
    elif request.user.is_authenticated:
        context["my_request"] = current_listing_request(listing.pk, request.user.pk)

    return render(request, "listing_detail.html", context)


@require_POST
@transaction.atomic
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing.objects.select_for_update(), pk=listing_id, author=request.user)

    if hasattr(listing, "engagement"):
        raise PermissionDenied("A listing with an engagement cannot be deleted.")

    listing.delete()
    return redirect("account_summary")


def edit_listing(request, listing_id):
    is_post = request.method == "POST"
    return_url = request.POST.get("next") if is_post else request.GET.get("next")

    if not url_has_allowed_host_and_scheme(
        return_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return_url = reverse("account_summary")

    with transaction.atomic() if is_post else nullcontext():
        listings = Listing.objects.filter(author=request.user)
        if is_post:
            listings = listings.select_for_update()

        listing = get_object_or_404(listings, pk=listing_id)
        form = CreateListingForm(request.POST if is_post else None, instance=listing)

        if hasattr(listing, "engagement"):
            form.fields["service_type"].disabled = True

        if is_post and form.is_valid():
            form.save()
            return redirect(return_url)

    return render(request, "edit_listing.html", {"form": form, "listing": listing, "return_url": return_url})