from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["nickname", "income", "expenses"]  # <-- include nickname
        widgets = {
            "nickname": forms.TextInput(attrs={"placeholder": "Optional nickname"}),
            "income": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "expenses": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }
        labels = {
            "nickname": "Nickname",
            "income": "Monthly Income",
            "expenses": "Monthly Expenses",
        }