
from django.db.models.signals import post_save
from django.dispatch import receiver
from investor.models import Investor
from investor.models import InvestmentOffer
from projectOwner.models import Project
from investor.models import Negotiation
from accounts.utils import notify_user, notify_users
from .models import Notification  
# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Review
from projectOwner.models import Project
from investor.models import InvestmentOffer
from .utils import update_user_rating
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import User
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




# تخزين الحالة القديمة قبل الحفظ
@receiver(pre_save, sender=User)
def cache_old_user_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            instance._was_active = old_instance.is_active
        except User.DoesNotExist:
            instance._was_active = False

# إرسال الإيميل إذا تغير is_active من False إلى True
@receiver(post_save, sender=User)
def notify_user_account_activated(sender, instance, created, **kwargs):
    if not created and not kwargs.get('raw', False):
        if not getattr(instance, '_was_active', True) and instance.is_active:
            subject = 'Account Activated'
            message = f'Hello {instance.full_name}, your account has been activated. You can now log in to your account.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [instance.email]
            send_mail(subject, message, from_email, recipient_list)



@receiver(post_save, sender=Project)
def update_owner_rating_on_project_status_change(sender, instance, **kwargs):
    if instance.status == 'closed':
        update_user_rating(instance.owner.user)

@receiver(post_save, sender=InvestmentOffer)
def update_investor_rating_on_offer_accept(sender, instance, **kwargs):
    if instance.status == 'accepted':
        update_user_rating(instance.investor.user)

@receiver(post_save, sender=Review)
def update_rating_on_review(sender, instance, created, **kwargs):
    if created:
        update_user_rating(instance.reviewed)

# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from accounts.models import Notification
from projectOwner.models import FeasibilityStudy

# User = get_user_model()

# @receiver(post_save, sender=FeasibilityStudy)
# def notify_admin_on_ai_score(sender, instance, created, **kwargs):
#     if instance.ai_score is not None:
#         admins = User.objects.filter(role='admin')
#         for admin in admins:
#             Notification.objects.create(
#                 user=admin,
#                 message=f"AI score reached: {instance.ai_score} for project {instance.project.title}"
#             )
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from accounts.models import Notification 
from projectOwner.models import ProjectOwner
 # عدّل هذا المسار حسب مكان الموديل عندك

@receiver(post_save, sender=Investor)
def notify_admin_on_investor_creation(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        role_display = 'Investor'
        
        # جمع معلومات إضافية
        additional_info = []
        if getattr(instance, 'company_name', None):
            additional_info.append(f"Company: {instance.company_name}")
        if getattr(instance, 'commercial_register', None):
            additional_info.append(f"Commercial Register: {instance.commercial_register}")
        if getattr(instance, 'phone_number', None):
            additional_info.append(f"Phone: {instance.phone_number}")
            
        # Notification message with user details
        details = " | ".join(additional_info) if additional_info else "Basic registration only"
        message = f"New account created ({role_display}) with name: {user.full_name}. {details}. View details: /api/new-user-detail/{user.id}/. ID:{user.id}"

        # Send notification to all admins
        admins = User.objects.filter(role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=message
            )

@receiver(post_save, sender=ProjectOwner)
def notify_admin_on_owner_creation(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        role_display = 'Project Owner'
        
        # جمع معلومات إضافية
        additional_info = []
        if getattr(instance, 'phone_number', None):
            additional_info.append(f"Phone: {instance.phone_number}")
        if getattr(instance, 'bio', None):
            additional_info.append(f"Bio: {instance.bio}")
            
        # Notification message with user details and API link
        details = " | ".join(additional_info) if additional_info else "No profile details provided"
        message = f"New account created ({role_display}) with name: {user.full_name}. {details}. View details: /api/new-user-detail/{user.id}/. ID:{user.id}"

        # Send notification to all admins
        admins = User.objects.filter(role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=message
            )