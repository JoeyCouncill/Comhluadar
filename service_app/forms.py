from django import forms
from .models import Service
from django.utils import timezone

class ServiceForm(forms.ModelForm):
	class Meta:
		model = Service
		fields = ['listing_type', 'title', 'category', 'date']

	def clean_date(self):
		date = self.cleaned_data['date']

		if date < timezone.localdate():
			raise forms.ValidationError('Service date cannot be in the past.')

		return date