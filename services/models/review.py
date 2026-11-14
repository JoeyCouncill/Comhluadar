from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Review(models.Model):
    class Role(models.TextChoices):
        PROVIDER = "provider"
        RECIPIENT = "recipient"

    listing = models.ForeignKey(
        "services.Listing",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
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
    reviewed_role = models.CharField(
        max_length=10,
        choices=Role.choices,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "reviewer", "reviewed_user"],
                name="unique_review_per_listing_pair",
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    reviewer=models.F("reviewed_user")
                ),
                name="review_prevent_self",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_range",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    reviewed_role__in=["provider", "recipient"]
                ),
                name="review_valid_role",
            ),

        ]

    def clean(self):
        super().clean()

        if not (
            self.listing_id
            and self.reviewer_id
            and self.reviewed_user_id
        ):
            return

        listing = self.listing

        if self.reviewer_id == self.reviewed_user_id:
            raise ValidationError("You cannot review yourself.")

        author_is_reviewed = (
            self.reviewed_user_id == listing.author_id
        )
        author_is_reviewer = (
            self.reviewer_id == listing.author_id
        )

        if not (author_is_reviewed or author_is_reviewer):
            raise ValidationError(
                "One person in this review must be the listing author."
            )

        if listing.service_type == "offer":
            author_role = self.Role.PROVIDER
            other_role = self.Role.RECIPIENT
        elif listing.service_type == "request":
            author_role = self.Role.RECIPIENT
            other_role = self.Role.PROVIDER
        else:
            raise ValidationError("The listing has an invalid service type.")

        expected_role = (
            author_role if author_is_reviewed else other_role
        )

        if self.reviewed_role != expected_role:
            raise ValidationError({
                "reviewed_role":
                    "This role does not match the listing and reviewed user."
            })

    def __str__(self):
        return (
            f"{self.reviewed_user}: "
            f"{self.rating}/5 {self.get_reviewed_role_display()}"
        )