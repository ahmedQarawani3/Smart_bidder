
from django.db.models.signals import post_save
from django.dispatch import receiver
from investor.models import Investor
from investor.models import InvestmentOffer
from projectOwner.models import Project
from investor.models import Negotiation
from accounts.utils import notify_user, notify_users

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

