from django import forms
from .models import FamilyGroup


class GroupJoinForm(forms.Form):
    code = forms.CharField(max_length=32)

    def clean_code(self):
        code = self.cleaned_data["code"]
        if not FamilyGroup.objects.filter(code=code).exists():
            raise forms.ValidationError("Invalid invite code")
        return code


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = FamilyGroup
        fields = ["name", "code"]

    def clean_code(self):
        code = self.cleaned_data["code"]
        if FamilyGroup.objects.filter(code=code).exists():
            raise forms.ValidationError("This code is already in use")
        return code
