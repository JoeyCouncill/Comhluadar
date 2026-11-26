from django.urls import path
from .views.profile import account_summary, edit_profile, front_page
from .views.authentication import create_account, user_login

urlpatterns = [
    path("", front_page, name="front_page"),
    path("create_account/", create_account, name="create_account"),
    path("user_login/", user_login, name="user_login"),
    path("account_summary/", account_summary, name="account_summary"),
    path("edit_profile/", edit_profile, name="edit_profile"),
    path("profile/<int:user_id>/", account_summary, name="user_profile"),
]