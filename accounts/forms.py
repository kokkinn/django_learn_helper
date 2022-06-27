from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserChangeForm
from django.core.exceptions import ValidationError

# from .utils import send_activation_notification

# from .apps import user_registered
# from .apps import user_registered
from .utils import send_activation_notification


class AccountRegistrationForm(forms.ModelForm):
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(
        label='Password:',
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html
    )
    password2 = forms.CharField(
        label='Confirm password:',
        widget=forms.PasswordInput,
        help_text='Please repeat password'
    )

    def clean_password1(self):
        pwd = self.cleaned_data['password1']
        if pwd:
            password_validation.validate_password(pwd)

        return pwd

    def clean(self):
        super().clean()
        pwd1 = self.cleaned_data['password1']
        pwd2 = self.cleaned_data['password2']
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise ValidationError(
                {
                    'password2': ValidationError('Password not equals', code='password_mismatch')
                }
            )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        user.is_activated = False
        if commit:
            user.save()

        send_activation_notification(user)
        # user_registered.send(AccountRegistrationForm, instance=user)

        return user

    class Meta:
        model = get_user_model()
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        )


class AccountUpdateForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'birthday',
            'city',
            'avatar',
        ]
