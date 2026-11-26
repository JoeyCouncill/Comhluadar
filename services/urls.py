from django.urls import path
from .views.listings import all_listings_view, delete_listing, edit_listing, listing_detail, new_listing
from .views.engagements import (
    decide_engagement_request,
    engagement_request_detail,
    request_engagement,
    start_engagement_chat,
    reopen_engagement_request,
    mark_engagement_complete,
    write_engagement_review,
)

urlpatterns = [
	path('all_listings_view/', all_listings_view, name='all_listings_view'),
	path('services/new_listing', new_listing, name='new_listing'),
    path('listing/<int:listing_id>', listing_detail, name='listing_detail'),
	path('listing/<int:listing_id>/edit', edit_listing, name='edit_listing'),
	path('listing/<int:listing_id>/delete', delete_listing, name='delete_listing'),
    path("listing/<int:listing_id>/engagement-requests/", request_engagement, name="request_engagement"),
    path("listing/<int:listing_id>/engagement/complete/", mark_engagement_complete, name="mark_engagement_complete"),
    path("listing/<int:listing_id>/engagement/review/", write_engagement_review, name="write_engagement_review"),
    path(
        "listing/<int:listing_id>/engagement-requests/<int:request_id>/",
        engagement_request_detail,
        name="engagement_request_detail",
    ),
    path(
        "listing/<int:listing_id>/engagement-requests/<int:request_id>/chat/",
        start_engagement_chat,
        name="start_engagement_chat",
    ),
    path(
        "listing/<int:listing_id>/engagement-requests/<int:request_id>/decision/",
        decide_engagement_request,
        name="decide_engagement_request",
    ),
    path(
        "listing/<int:listing_id>/engagement-requests/<int:request_id>/reopen/",
        reopen_engagement_request,
        name="reopen_engagement_request",
    ),
]