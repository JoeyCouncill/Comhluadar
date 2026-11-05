import os
from .base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = ["3.139.58.17"]
CSRF_TRUSTED_ORIGINS = ["https://3.139.58.17"]

STATIC_URL = "static/"

MEDIA_URL = "/media/"