from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserReview(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    reviewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "reviewed_user"],
                name="unique_user_review",
            ),
            models.CheckConstraint(
                condition=~models.Q(reviewer=models.F("reviewed_user")),
                name="prevent_self_review",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="user_rating_between_1_and_5",
            ),
        ]