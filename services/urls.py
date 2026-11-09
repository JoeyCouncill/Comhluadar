from django.urls import path
from .views.listings import *

urlpatterns = [
	path('all_listings_view/', all_listings_view, name='all_listings_view'),
	path('services/new_listing', new_listing, name='new_listing'),
	path('post/<int:post_id>', listing_detail, name='listing_detail'),
]
