from django.utils.http import url_has_allowed_host_and_scheme
from notifications.models import Notification


def is_local_target(url):
    return (
        url.startswith("/")
        and not url.startswith("//")
        and url_has_allowed_host_and_scheme(url, allowed_hosts=set())
    )


def notify(*, recipient, text, url=""):
    if url and not is_local_target(url):
        raise ValueError("The notification destination must be a local path.")

    return Notification.objects.create(recipient=recipient, text=text, target_url=url)