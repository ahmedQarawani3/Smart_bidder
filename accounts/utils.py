from .models import Notification

def notify_user(user, message):
    Notification.objects.create(user=user, message=message)

def notify_users(users, message):
    for user in users:
        Notification.objects.create(user=user, message=message)
