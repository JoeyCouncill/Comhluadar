from django.db import models

service_types = [
	('Tutoring', 'Tutoring'),
	('Specialized Labor', 'Specialized Labor'),
	('General Labor', 'General Labor')
	]

class Service(models.Model):
	name = models.CharField(max_length=100)
	category = models.CharField(max_length=50, choices=service_types, blank=True)
	date = models.DateField()

	def __str__(self):
		return self.name
