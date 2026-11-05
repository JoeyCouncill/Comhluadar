import os
from .base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ["DJANGO_ALLOWED_HOSTS"].split(",")
    if host.strip()

]

CSRF_TRUSTED_ORIGINS = ["https://comhluadar.com",
                        "www.comhluadar.com",
                        ]

STATIC_URL = "static/"

MEDIA_URL = "/media/"