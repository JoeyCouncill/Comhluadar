from django.urls import path
from .views import * 

urlpatterns = [
    path("", front_page, name="front_page"),
    path("create_account/", create_account, name="create_account"),
    path("user_login/", user_login, name="user_login"),
    path("account_summary/", account_summary, name="account_summary"),

]