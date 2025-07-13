# adminAccounts/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from accounts.models import Notification, User
from projectOwner.models import Project
from investor.models import InvestmentOffer, Negotiation
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Complaint
from accounts.models import Notification, User
# ✅ إحضار جميع الأدمنات النشطين
def get_admin_users():
    return User.objects.filter(role='admin', is_active=True)

# ✅ إشعار عند تحديث أو إنشاء مشروع
@receiver(post_save, sender=Project)
def notify_admin_project_updated(sender, instance, created, **kwargs):
    message = f"{'تم إنشاء' if created else 'تم تحديث'} المشروع: {instance.title}"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# ✅ إشعار عند حذف مشروع
@receiver(post_delete, sender=Project)
def notify_admin_project_deleted(sender, instance, **kwargs):
    message = f"تم حذف المشروع: {instance.title}"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# ✅ إشعار عند تحديث أو إنشاء عرض استثماري
@receiver(post_save, sender=InvestmentOffer)
def notify_admin_offer_updated(sender, instance, created, **kwargs):
    message = f"{'تم إنشاء' if created else 'تم تعديل'} عرض استثماري بقيمة {instance.amount} لمشروع: {instance.project.title}"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# ✅ إشعار عند حذف عرض استثماري
@receiver(post_delete, sender=InvestmentOffer)
def notify_admin_offer_deleted(sender, instance, **kwargs):
    message = f"تم حذف عرض استثماري لمشروع: {instance.project.title}"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# ✅ إشعار عند بدء مفاوضة جديدة
@receiver(post_save, sender=Negotiation)
def notify_admin_negotiation_started(sender, instance, created, **kwargs):
    if created:
        message = f"تم بدء مفاوضة جديدة على مشروع: {instance.offer.project.title} من قبل {instance.sender.full_name}"
        for admin in get_admin_users():
            Notification.objects.create(user=admin, message=message)

            
@receiver(post_save, sender=Complaint)
def notify_admins_on_new_complaint(sender, instance, created, **kwargs):
    if created:
        admins = User.objects.filter(role='admin', is_active=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"تم تقديم شكوى جديدة من المستخدم {instance.complainant.full_name} ضد {instance.defendant.full_name}."
            )