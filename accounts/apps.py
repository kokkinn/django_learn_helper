
from django.apps import AppConfig
from django.apps import AppConfig

from django.dispatch import Signal, receiver

from .utils import send_activation_notification


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    # def ready(self):
    #     from .signals import custom_user_pre_save
    #     pre_save.connect(custom_user_pre_save, sender=CustomUser)


user_registered = Signal()


def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registered.connect(user_registered_dispatcher)
