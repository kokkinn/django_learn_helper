from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from accounts.models import Profile


class AccountRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ["username", "first_name", "last_name", "email"]


class AccountUpdateForm(UserChangeForm):
    password = None

    class Meta(UserCreationForm.Meta):
        fields = [
            "first_name",
            "last_name",
            "email",

        ]


class AccountProfileUpdate(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["birthday", "city", ]
        widgets = {"birthday": forms.DateInput(attrs={"type": "date"})}
