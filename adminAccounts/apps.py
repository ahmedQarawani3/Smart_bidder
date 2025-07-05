# adminAccounts/apps.py

from django.apps import AppConfig

class AdminaccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminAccounts'

    def ready(self):
        import adminAccounts.signals
