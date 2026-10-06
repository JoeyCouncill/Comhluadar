from django.urls import path
from .views import *

urlpatterns = [
	path('inbox/', user_inbox, name='user_inbox'),
]
