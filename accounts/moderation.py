
from django.db.models import Q

from accounts.models import UserBlock


def users_are_blocked(user_a, user_b):
    """True if either user has blocked the other."""
    return UserBlock.objects.filter(
        Q(blocker=user_a, blocked=user_b)
        | Q(blocker=user_b, blocked=user_a)
    ).exists()
