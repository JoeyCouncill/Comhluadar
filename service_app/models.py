from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


service_types = [
	('Tutoring', 'Tutoring'),
	('Specialized Labor', 'Specialized Labor'),
	('General Labor', 'General Labor')
	]

class Service(models.Model):
	class ListingType(models.TextChoices):
		OFFER = "offer", "Offering a service"
		REQUEST = "request", "Requesting a service"

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="services",
	)

	listing_type = models.CharField(choices=ListingType.choices)

	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	category = models.CharField(
		max_length=50,
		choices=service_types,
		blank=True,
	)

	date = models.DateField()

	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

class ServiceReview(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["service", "reviewer"],
                name="unique_service_review",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="service_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"Service {self.service_id}: {self.rating}/5"