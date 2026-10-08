from django.urls import path
from .views import *

urlpatterns = [
	path('all_posts_view/', all_posts_view, name='all_posts_view'),
	path('service/new_post', new_post, name='new_post'),
]
