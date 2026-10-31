from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from services.models import Listing

class ServiceReview(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "reviewer"],
                name="unique_listing_review",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="listing_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"Service {self.listing_id}: {self.rating}/5"