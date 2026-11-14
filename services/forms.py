from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
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

class ReviewForm(forms.Form):
    reviewed_user = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        label="Person you are reviewing",
    )
    rating = forms.TypedChoiceField(
        choices=[(number, f"{number}/5") for number in range(1, 6)],
        coerce=int,
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, listing, reviewer, **kwargs):
        super().__init__(*args, **kwargs)

        users = get_user_model().objects

        if reviewer.pk == listing.author_id:
            self.fields["reviewed_user"].queryset = (
                users.exclude(pk=reviewer.pk)
                .order_by("username")
            )
        else:
            self.fields["reviewed_user"].queryset = users.filter(
                pk=listing.author_id
            )
            self.fields["reviewed_user"].initial = listing.author_id
            self.fields["reviewed_user"].widget = forms.HiddenInput()
