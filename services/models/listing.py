from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


service_types = [
	('Tutoring', 'Tutoring'),
	('Specialized Labor', 'Specialized Labor'),
	('General Labor', 'General Labor')
	]

class Listing(models.Model):
	class ListingType(models.TextChoices):
		OFFER = "offer", "Offering a service"
		REQUEST = "request", "Requesting a service"

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="listings",
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
