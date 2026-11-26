from django import forms
from django.utils import timezone
from .models import Listing

class CreateListingForm(forms.ModelForm):

    
    class Meta:
        model = Listing
        fields = ["service_type", "title", "description", "category", "date"]
        labels = {
            "service_type": "Service Type",
            "title": "Service Title",
            "description": "Service Description",
            "category": "Service Category",
            "date": "Service Date",
        }

        widgets = {
            "service_type": forms.Select(attrs={"id": "service_type", "class": "form-select"}),
            "title": forms.TextInput(attrs={"id": "title", "class": "form-control"}),
            "description": forms.Textarea(attrs={"id": "description", "class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"id": "category", "class": "form-select"}),
            "date": forms.DateInput(format="%Y-%m-%d", attrs={"id": "date", "type": "date", "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date < timezone.localdate():
            raise forms.ValidationError("Service date cannot be in the past.")
        return date

class ReviewForm(forms.Form):
    rating = forms.TypedChoiceField(
        choices=[("", "Choose a rating")]
        + [(number, f"{number}/5") for number in range(1, 6)],
        coerce=int,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    comment = forms.CharField(required=False, max_length=1000, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))


class EngagementRoundForm(forms.Form):
    decision_round = forms.IntegerField(min_value=1)
