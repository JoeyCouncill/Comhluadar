from django import forms
from .models import Profile


class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)

    class Meta:
        model = Profile
        fields = [
            "profile_picture", 
            "cover_photo", 
            "skills", 
            "other_skill", 
            "interests", 
            "bio",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial["first_name"] = user.first_name
        self.initial["last_name"] = user.last_name

    def clean(self):
        cleaned_data = super().clean()

        for field_name in ["profile_picture", "cover_photo"]:
            image = cleaned_data.get(field_name)
            if image and image.size > 5 * 1024 * 1024:
                self.add_error(
                    field_name,
                    "Images must be under 5 MB.",
                )

        if cleaned_data.get("skills") == "other":
            if not cleaned_data.get("other_skill"):
                self.add_error(
                    "other_skill",
                    "Please describe your other skill.",
                )
        else:
            cleaned_data["other_skill"] = ""

        return cleaned_data