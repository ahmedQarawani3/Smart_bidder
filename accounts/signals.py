
from django.db.models.signals import post_save
from django.dispatch import receiver
from investor.models import Investor
from investor.models import InvestmentOffer
from projectOwner.models import Project
from investor.models import Negotiation
from accounts.utils import notify_user, notify_users
from .models import Notification  

# ✅ إشعار تلقائي عند إنشاء مشروع جديد
@receiver(post_save, sender=Project)
def notify_new_project(sender, instance, created, **kwargs):
    if created:
        investors = Investor.objects.all()
        message = f"New project '{instance.title}' matches your investment interests"
        notify_users([inv.user for inv in investors], message)

# ✅ إشعار تلقائي عند تغيير حالة عرض الاستثمار
@receiver(post_save, sender=InvestmentOffer)
def notify_offer_status_change(sender, instance, **kwargs):
    if instance.status == 'accepted':
        message = f"Your offer of ${instance.amount} for '{instance.project.title}' has been accepted"
        notify_user(instance.investor.user, message)

    elif instance.status == 'rejected':
        message = f"Your offer for '{instance.project.title}' was not accepted. Consider revising your terms."
        notify_user(instance.investor.user, message)

# ✅ إشعار عند بدء التفاوض بين المستثمر وصاحب المشروع
@receiver(post_save, sender=Negotiation)
def notify_negotiation_started(sender, instance, created, **kwargs):
    if created:
        offer = instance.offer
        other_party = offer.project.owner.user if instance.sender == offer.investor.user else offer.investor.user
        message = f"{instance.sender.full_name} wants to negotiate terms for your investment offer"
        notify_user(other_party, message)

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User

@receiver(post_save, sender=User)
def notify_user_account_activated(sender, instance, created, **kwargs):
    if not created:
        # فقط إذا صار تفعيل جديد
        old_user = User.objects.filter(pk=instance.pk).first()
        if old_user and not kwargs.get('raw', False):  # ignore during fixtures
            if not old_user.is_active and instance.is_active:
                subject = 'Account Activated'
                message = f'Hello {instance.full_name}, your account has been activated. You can now log in to your account.'
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [instance.email]
                send_mail(subject, message, from_email, recipient_list)

