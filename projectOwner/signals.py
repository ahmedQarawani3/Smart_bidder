from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from accounts.utils import notify_user, notify_users, update_user_rating
from investor.models import InvestmentOffer, Negotiation
from projectOwner.models import Project, FeasibilityStudy
from accounts.models import Notification, User, Review

# -- 1. إشعار عند استلام عرض استثماري جديد --
@receiver(post_save, sender=InvestmentOffer)
def notify_new_investment_offer(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        message = f"Your project '{instance.project.title}' has received a new investment offer worth {instance.amount}."
        Notification.objects.create(user=instance.project.owner.user, message=message)

# -- 2. إشعار لصاحب المشروع عند قبول عرض --
@receiver(post_save, sender=InvestmentOffer)
def notify_offer_accepted(sender, instance, **kwargs):
    if instance.status == 'accepted' and not hasattr(instance, '_accepted_notified'):
        instance._accepted_notified = True
        message = f"The investment offer from '{instance.investor.user.full_name}' for your project '{instance.project.title}' has been accepted."
        Notification.objects.create(user=instance.project.owner.user, message=message)

# -- 3. إشعار للمستثمرين عند رفض عروضهم بسبب تحديث المشروع --
def notify_rejected_offers_due_to_project_update(project):
    offers = InvestmentOffer.objects.filter(project=project, status='rejected', rejection_reason__isnull=True)
    for offer in offers:
        offer.rejection_reason = 'project_update'
        offer.save(update_fields=['rejection_reason'])
        message = f"Your investment offer for the project '{project.title}' has been rejected because the project data has changed."
        Notification.objects.create(user=offer.investor.user, message=message)

# -- 4. إشعار قبل 3 أيام من إغلاق المشروع تلقائيًا --
def notify_project_owner_before_closing():
    projects = Project.objects.filter(status='active')
    for project in projects:
        offers = InvestmentOffer.objects.filter(project=project).order_by('created_at')
        if not offers.exists():
            continue
        deadline = offers.first().created_at + timedelta(days=20)
        remaining = (deadline - timezone.now()).days
        if remaining == 3:
            message = f"Only 3 days left to select an investment offer for your project '{project.title}' before automatic closure."
            Notification.objects.create(user=project.owner.user, message=message)

# -- 5. إشعار عند بدء تفاوض جديد --
@receiver(post_save, sender=Negotiation)
def notify_negotiation_started(sender, instance, created, **kwargs):
    if created:
        offer = instance.offer
        other_party = offer.project.owner.user if instance.sender == offer.investor.user else offer.investor.user
        message = f"{instance.sender.full_name} has initiated a negotiation on the investment offer for the project '{offer.project.title}'."
        Notification.objects.create(user=other_party, message=message)

# -- 6. إشعار لصاحب المشروع عند تغيير الحالة --
@receiver(post_save, sender=Project)
def notify_project_status_change(sender, instance, created, **kwargs):
    if not created:
        previous = Project.objects.filter(pk=instance.pk).first()
        if previous and previous.status != instance.status:
            message = f"The status of your project '{instance.title}' has been updated to: {instance.status}"
            Notification.objects.create(user=instance.owner.user, message=message)

# -- 7. إشعار للأدمن عند إنشاء أو تعديل مشروع --
def get_admin_users():
    return User.objects.filter(role='admin', is_active=True)

@receiver(post_save, sender=Project)
def notify_admin_project_created_or_edited(sender, instance, created, **kwargs):
    if created:
        message = f"📌 مشروع جديد قيد الموافقة: {instance.title}"
    else:
        instance.status = 'pending'
        instance.save(update_fields=['status'])
        message = f"✏ تم تعديل المشروع '{instance.title}' من قبل صاحبه ويحتاج إلى موافقة جديدة."
    for admin in get_admin_users():
        Notification.objects.create(user=admin, message=message)

# -- 8. إشعار للأدمن عند تعديل دراسة الجدوى --
@receiver(post_save, sender=FeasibilityStudy)
def notify_admin_on_feasibility_update(sender, instance, created, **kwargs):
    if not created:
        project = instance.project
        project.status = 'pending'
        project.save(update_fields=['status'])
        message = f"📊 تم تعديل دراسة الجدوى الخاصة بالمشروع '{project.title}' ويحتاج إلى مراجعة."
        for admin in get_admin_users():
            Notification.objects.create(user=admin, message=message)

# -- 9. إشعار للمستثمر عند قبول أو رفض عرضه --
@receiver(post_save, sender=InvestmentOffer)
def notify_offer_status_change(sender, instance, **kwargs):
    if instance.status == 'accepted':
        message = f"Your offer of ${instance.amount} for '{instance.project.title}' has been accepted"
        notify_user(instance.investor.user, message)
    elif instance.status == 'rejected':
        message = f"Your offer for '{instance.project.title}' was not accepted. Consider revising your terms."
        notify_user(instance.investor.user, message)

# -- 10. تحديث تقييم المستثمر عند قبول عرضه --
@receiver(post_save, sender=InvestmentOffer)
def update_investor_rating_on_offer_accept(sender, instance, **kwargs):
    if instance.status == 'accepted':
        update_user_rating(instance.investor.user)

# -- 11. تحديث تقييم المستخدم عند إنشاء تقييم (Review) --
@receiver(post_save, sender=Review)
def update_rating_on_review(sender, instance, created, **kwargs):
    if created:
        update_user_rating(instance.reviewed)