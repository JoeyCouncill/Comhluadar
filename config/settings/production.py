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

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"].split(",")
    if origin.strip()
    ]

STATIC_URL = "static/"

MEDIA_URL = "/media/"

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": {
            "host": os.environ["EMAIL_HOST"],
            "port": 587,
            "username": os.environ["EMAIL_HOST_USER"],
            "password": os.environ["EMAIL_HOST_PASSWORD"],
            "use_tls": True,
            "timeout": 15,
        },
    },
}

DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]