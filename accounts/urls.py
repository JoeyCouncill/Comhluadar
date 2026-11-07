from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views.profile import * 
from .views.authentication import *

urlpatterns = [
    path("", front_page, name="front_page"),
    path("registration/signup/", signup, name="signup"),
    path("registration/login/", login, name="login"),
    path("account_summary/", account_summary, name="account_summary"),
    path("edit_profile/", edit_profile, name="edit_profile"),
    path("registration/", include("django.contrib.auth.urls")),
]