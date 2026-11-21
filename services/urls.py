from django.urls import path
from .views.listings import *

urlpatterns = [
	path('all_listings_view/', all_listings_view, name='all_listings_view'),
	path('services/new_listing', new_listing, name='new_listing'),
    path('listing/<int:listing_id>', listing_detail, name='listing_detail'),
	path('listing/<int:listing_id>/edit', edit_listing, name='edit_listing'),
	path('listing/<int:listing_id>/delete', delete_listing, name='delete_listing'),
]