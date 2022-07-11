from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.core.signing import BadSignature
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from django_learn_helper import settings
from .forms import AccountRegistrationForm
from .forms import AccountUpdateForm
from .utils import signer


class AccountRegistrationView(CreateView):
    model = get_user_model()
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('accounts:registration_done')
    form_class = AccountRegistrationForm


class AccountRegistrationDoneView(TemplateView):
    template_name = 'accounts/registration_done.html'


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'accounts/bad_signature.html')

    user = get_object_or_404(get_user_model(), username=username)
    if user.is_activated:
        template = 'accounts/user_is_activated.html'
    else:
        template = 'accounts/activation_done.html'
        user.is_active = True
        user.is_activated = True
        apps.get_model("words.GroupOfWords").objects.create(name="General", user=user)
        print("User created")
    user.save()

    return render(request, template)


class AccountLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_redirect_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url

        return reverse('index')


class AccountLogoutView(LogoutView):
    template_name = 'accounts/logout.html'


def account_profile_view(request):
    return render(request, 'accounts/profile.html')


class AccountUpdateProfileView(UpdateView):
    template_name = 'accounts/profile_update.html'
    model = get_user_model()
    success_url = reverse_lazy('accounts:profile')
    form_class = AccountUpdateForm

    def get_object(self, queryset=None):
        return self.request.user


def send_me_mail(request):
    from django.core.mail import send_mail
    # user_email = request.user.email
    send_mail(
        'Test mail',
        'I just wanted to say that you are fucking asshole',
        settings.EMAIL_HOST_USER,
        ["kokkin.george@gmail.com"],
        fail_silently=False
    )
    return render(request, "accounts/thank_you.html")

