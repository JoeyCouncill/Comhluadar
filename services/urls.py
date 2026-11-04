from django.urls import path
from .views.listings import *

urlpatterns = [
	path('all_posts_view/', all_posts_view, name='all_posts_view'),
	path('services/new_post', new_post, name='new_post'),
]
