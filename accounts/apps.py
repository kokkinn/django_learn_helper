from django.apps import AppConfig
from django.apps import AppConfig
from django.dispatch import Signal, receiver

from .utils import send_activation_notification


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'


user_registered = Signal()


def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registered.connect(user_registered_dispatcher)
