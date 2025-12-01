from django import forms
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["nickname", "income", "expenses"]
        labels = {
            "nickname": "Nickname",
            "income": "Monthly Income",
            "expenses": "Monthly Expenses",
        }


class JoinGroupForm(forms.Form):
    code = forms.CharField(label="Family Code", max_length=10)