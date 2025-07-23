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

# ✅ Notify when a project is created or updated
from django.db.models.signals import post_save
from django.dispatch import receiver
from projectOwner.models import Project
from accounts.models import User,Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User

def get_admin_users():
    return User.objects.filter(role='admin')

@receiver(post_save, sender=Project)
def notify_admin_project_updated(sender, instance, created, **kwargs):
    # نتجاهل إذا كانت الحالة أصبحت active أو closed => يعني تمت الموافقة أو الرفض
    if not created and instance.status in ['active', 'closed']:
        return  # لا ترسل إشعار في حال الموافقة أو الرفض

    message = f"{'تم إنشاء مشروع جديد:' if created else 'تم تعديل المشروع:'} {instance.title} [ID: {instance.id}]"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)




# ✅ Notify when a project is deleted
@receiver(post_delete, sender=Project)
def notify_admin_project_deleted(sender, instance, **kwargs):
    message = f"Project deleted: {instance.title}"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# ✅ Notify when an investment offer is created or updated
@receiver(post_save, sender=InvestmentOffer)
def notify_admin_offer_updated(sender, instance, created, **kwargs):
    message = f"{'Investment offer created' if created else 'Investment offer updated'} with amount {instance.amount} for project: {instance.project.title}"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# ✅ Notify when an investment offer is deleted
@receiver(post_delete, sender=InvestmentOffer)
def notify_admin_offer_deleted(sender, instance, **kwargs):
    message = f"Investment offer deleted for project: {instance.project.title}"
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# ✅ Notify when a new negotiation is started
@receiver(post_save, sender=Negotiation)
def notify_admin_negotiation_started(sender, instance, created, **kwargs):
    if created:
        message = f"A new negotiation started for project: {instance.offer.project.title} by {instance.sender.full_name}"
        for admin in get_admin_users():
            Notification.objects.create(user=admin, message=message)

# ✅ Notify when a new complaint is submitted
@receiver(post_save, sender=Complaint)
def notify_admins_on_new_complaint(sender, instance, created, **kwargs):
    if created:
        admins = User.objects.filter(role='admin', is_active=True)
        for admin in admins:
            Notification.objects.create(
                user=admin,
                message=f"A new complaint was submitted by {instance.complainant.full_name} against {instance.defendant.full_name}."
            )
