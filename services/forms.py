from django import forms
from django.utils import timezone
from .models import Listing

class CreateListingForm(forms.ModelForm):
	class Meta:
		model = Listing
		fields = ['service_type', 'title', 'category', 'date']

	def clean_date(self):
		date = self.cleaned_data['date']

		if date < timezone.localdate():
			raise forms.ValidationError('Service date cannot be in the past.')

		return date
