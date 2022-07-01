from django.apps import AppConfig
import accounts.signals


class WordsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'words'
