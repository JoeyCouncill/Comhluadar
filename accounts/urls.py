from django.urls import path
from .views.profile import account_summary, edit_profile, front_page
from .views.authentication import create_account, user_login
from .views.moderation import block_user, unblock_user, report_user

urlpatterns = [
    path("", front_page, name="front_page"),
    path("create_account/", create_account, name="create_account"),
    path("user_login/", user_login, name="user_login"),
    path("account_summary/", account_summary, name="account_summary"),
    path("edit_profile/", edit_profile, name="edit_profile"),
    path("profile/<int:user_id>/", account_summary, name="user_profile"),
    path("profile/<int:user_id>/block/", block_user, name="block_user"),
    path("profile/<int:user_id>/unblock/", unblock_user, name="unblock_user"),
    path("profile/<int:user_id>/report/", report_user, name="report_user"),
]