from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


service_types = [
	('Tutoring', 'Tutoring'),
	('Specialized Labor', 'Specialized Labor'),
	('General Labor', 'General Labor')
	]

class Listing(models.Model):
	class ServiceType(models.TextChoices):
		OFFER = "offer", "Offering a service"
		REQUEST = "request", "Requesting a service"

	author = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="listings",
	)

	service_type = models.CharField(choices=ServiceType.choices)

	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	category = models.CharField(
		max_length=50,
		choices=service_types,
		blank=True,
	)

	date = models.DateField()

	created_at = models.DateTimeField(auto_now_add=True)

	def review_role_for(self, reviewed_user_id):
		if self.service_type not in self.ServiceType.values:
			raise ValidationError("The listing has an invalid service type.")
		author_is_provider = self.service_type == self.ServiceType.OFFER
		reviewing_author = reviewed_user_id == self.author_id

		if reviewing_author:
			return "provider" if author_is_provider else "recipient"
		
		return "recipient" if author_is_provider else "provider"

	def __str__(self):
		return self.title