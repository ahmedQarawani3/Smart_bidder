from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from accounts.utils import notify_user, notify_users

from investor.models import InvestmentOffer, Negotiation
from projectOwner.models import Project
from accounts.models import User
from accounts.models import Notification

# -- 1. Notification when a new investment offer is submitted --
@receiver(post_save, sender=InvestmentOffer)
def notify_new_investment_offer(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        project_owner_user = instance.project.owner.user
        message = f"Your project '{instance.project.title}' has received a new investment offer worth {instance.amount}."
        Notification.objects.create(user=project_owner_user, message=message)

# -- 2. Notification when an investment offer is accepted --
@receiver(post_save, sender=InvestmentOffer)
def notify_offer_accepted(sender, instance, **kwargs):
    if instance.status == 'accepted':
        message = f"The investment offer from '{instance.investor.user.full_name}' for your project '{instance.project.title}' has been accepted."
        Notification.objects.create(user=instance.project.owner.user, message=message)

# -- 3. Notification when all offers are rejected (e.g., due to project update or expiration) --
def notify_rejected_offers_due_to_project_update(project):
    offers = InvestmentOffer.objects.filter(project=project, status='rejected', rejection_reason__isnull=True)
    for offer in offers:
        # تعيين سبب الرفض (اختياري لو ضفت الحقل في الموديل)
        offer.rejection_reason = 'project_update'
        offer.save(update_fields=['rejection_reason'])

        message = f"Your investment offer for the project '{project.title}' has been rejected because the project data has changed."
        Notification.objects.create(user=offer.investor.user, message=message)


# -- 4. Notification when 3 days are left before the auto-close deadline --
def notify_project_owner_before_closing():
    check_date = timezone.now() + timedelta(days=3)
    projects = Project.objects.filter(status='active')
    for project in projects:
        offers = InvestmentOffer.objects.filter(project=project, created_at__isnull=False).order_by('created_at')
        if not offers.exists():
            continue
        first_offer_date = offers.first().created_at
        deadline = first_offer_date + timedelta(days=20)
        remaining = (deadline - timezone.now()).days
        if remaining == 3:
            message = f"Only 3 days left to select an investment offer for your project '{project.title}' before automatic closure."
            Notification.objects.create(user=project.owner.user, message=message)

# -- 5. Notification when a negotiation starts --
# ✅ Notify the other party when a negotiation is initiated
@receiver(post_save, sender=Negotiation)
def notify_negotiation_started(sender, instance, created, **kwargs):
    if created:
        offer = instance.offer
        other_party = offer.project.owner.user if instance.sender == offer.investor.user else offer.investor.user
        message = f"{instance.sender.full_name} has initiated a negotiation on the investment offer for the project '{offer.project.title}'."
        Notification.objects.create(user=other_party, message=message)

# ✅ Notify the project owner when the project status changes
@receiver(post_save, sender=Project)
def notify_project_status_change(sender, instance, created, **kwargs):
    if not created:
        previous = Project.objects.filter(pk=instance.pk).first()
        if previous and previous.status != instance.status:
            message = f"The status of your project '{instance.title}' has been updated to: {instance.status}"
            Notification.objects.create(user=instance.owner.user, message=message)


from projectOwner.models import Project, FeasibilityStudy
def get_admin_users():
    return User.objects.filter(role='admin', is_active=True)

@receiver(post_save, sender=Project)
def notify_admin_project_created_or_edited(sender, instance, created, **kwargs):
    if created:
        message = f"📌 مشروع جديد قيد الموافقة: {instance.title}"
    else:
        instance.status = 'pending'
        instance.save(update_fields=['status'])

        message = f"✏️ تم تعديل المشروع '{instance.title}' من قبل صاحبه ويحتاج إلى موافقة جديدة."

    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

@receiver(post_save, sender=FeasibilityStudy)
def notify_admin_on_feasibility_update(sender, instance, created, **kwargs):
    project = instance.project
    if not created:
        project.status = 'pending'
        project.save(update_fields=['status'])

        message = f"📊 تم تعديل دراسة الجدوى الخاصة بالمشروع '{project.title}' ويحتاج إلى مراجعة."

        for admin in get_admin_users():
            Notification.objects.create(user=admin, message=message)

