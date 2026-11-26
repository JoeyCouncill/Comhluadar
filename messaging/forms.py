from django import forms


class MessageForm(forms.Form):
    body = forms.CharField(
        label="Message",
        max_length=2000,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))


class MarkChatSeenForm(forms.Form):
    seen_through = forms.IntegerField(min_value=0, max_value=2**63 - 1)