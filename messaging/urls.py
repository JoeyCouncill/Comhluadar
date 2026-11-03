from django.urls import path
from .views.inbox import *

urlpatterns = [
	path('inbox/', inbox, name='inbox'),
]
