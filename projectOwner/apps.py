from django.apps import AppConfig


class ProjectownerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projectOwner'

    def ready(self):
        import projectOwner.signals  # تأكد من المسار صحيح
