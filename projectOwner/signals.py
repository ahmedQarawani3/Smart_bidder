from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from accounts.utils import notify_user, notify_users, update_user_rating
from investor.models import InvestmentOffer, Negotiation
from projectOwner.models import Project, FeasibilityStudy
from accounts.models import Notification, User, Review


# 1- إشعار + تحديث تقييم + إشعار عند تغيير InvestmentOffer
@receiver(post_save, sender=InvestmentOffer)
def handle_investment_offer_notifications(sender, instance, created, **kwargs):
    if hasattr(instance, '_signal_handled'):
        return
    instance._signal_handled = True

    if created and instance.status == 'pending':
        message = f"Your project '{instance.project.title}' has received a new investment offer worth {instance.amount}."
        Notification.objects.create(user=instance.project.owner.user, message=message)

    if instance.status == 'accepted':
        message_owner = f"The investment offer from '{instance.investor.user.full_name}' for your project '{instance.project.title}' has been accepted."
        Notification.objects.create(user=instance.project.owner.user, message=message_owner)

        message_investor = f"Your offer of ${instance.amount} for '{instance.project.title}' has been accepted."
        notify_user(instance.investor.user, message_investor)

        update_user_rating(instance.investor.user)

    elif instance.status == 'rejected':
        message = f"Your offer for '{instance.project.title}' was not accepted. Consider revising your terms."
        notify_user(instance.investor.user, message)


# 2- إشعار عند رفض العروض بسبب تعديل المشروع
def notify_rejected_offers_due_to_project_update(project):
    offers = InvestmentOffer.objects.filter(project=project, status='rejected', rejection_reason__isnull=True)
    for offer in offers:
        offer.rejection_reason = 'project_update'
        offer.save(update_fields=['rejection_reason'])
        message = f"Your investment offer for the project '{project.title}' has been rejected because the project data has changed."
        Notification.objects.create(user=offer.investor.user, message=message)


# 3- إشعار قبل 3 أيام من الإغلاق التلقائي للمشروع
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


# 4- إشعار عند بدء تفاوض جديد
@receiver(post_save, sender=Negotiation)
def notify_negotiation_started(sender, instance, created, **kwargs):
    if created:
        offer = instance.offer
        other_party = offer.project.owner.user if instance.sender == offer.investor.user else offer.investor.user
        message = f"{instance.sender.full_name} has initiated a negotiation on the investment offer for the project '{offer.project.title}'."
        Notification.objects.create(user=other_party, message=message)


# 5- إشعار لصاحب المشروع عند تغيير الحالة
@receiver(post_save, sender=Project)
def notify_project_status_change(sender, instance, created, **kwargs):
    if not created:
        previous = Project.objects.filter(pk=instance.pk).first()
        if previous and previous.status != instance.status:
            message = f"The status of your project '{instance.title}' has been updated to: {instance.status}"
            Notification.objects.create(user=instance.owner.user, message=message)

#يلي تحت كلو وقت يعدل مشروغ

# 6- إشعار الأدمن عند إنشاء أو تعديل مشروع (بدون تعديل الحالة)
# signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

# Temporary cache for old instances before saving
OLD_PROJECTS_CACHE = {}
OLD_FEASIBILITY_CACHE = {}

def get_admin_users():
    return User.objects.filter(role='admin', is_active=True)

@receiver(pre_save, sender=Project)
def cache_old_project(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            OLD_PROJECTS_CACHE[instance.pk] = {
                'title': old_instance.title,
                'description': old_instance.description,
                'status': old_instance.status,
                'idea_summary': old_instance.idea_summary,
                'problem_solving': old_instance.problem_solving,
                'category': old_instance.category,
                'readiness_level': old_instance.readiness_level,
                'image': old_instance.image.url if old_instance.image else None,
            }
        except sender.DoesNotExist:
            pass

@receiver(pre_save, sender=FeasibilityStudy)
def cache_old_feasibility(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            OLD_FEASIBILITY_CACHE[instance.pk] = {
                'current_revenue': old_instance.current_revenue,
                'funding_required': old_instance.funding_required,
                'marketing_investment_percentage': old_instance.marketing_investment_percentage,
                'team_investment_percentage': old_instance.team_investment_percentage,
                'expected_monthly_revenue': old_instance.expected_monthly_revenue,
                'roi_period_months': old_instance.roi_period_months,
                'expected_profit_margin': old_instance.expected_profit_margin,
                'growth_opportunity': old_instance.growth_opportunity,
            }
        except sender.DoesNotExist:
            pass

@receiver(post_save, sender=Project)
def notify_admin_project_created_or_edited(sender, instance, created, **kwargs):
    if created:
        message = f"📌 New project awaiting approval: {instance.title}"
        for admin in get_admin_users():
            Notification.objects.create(user=admin, message=message)
    else:
        old_data = OLD_PROJECTS_CACHE.pop(instance.pk, None)
        if not old_data:
            return

        changes = []
        fields_to_check = ['title', 'description', 'status', 'idea_summary', 'problem_solving', 'category', 'readiness_level']

        for field in fields_to_check:
            old_value = old_data.get(field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changes.append(f"✏ Field '{field}' changed from '{old_value}' to '{new_value}'")

        old_image = old_data.get('image')
        new_image = instance.image.url if instance.image else None
        if old_image != new_image:
            changes.append(f"✏ Field 'image' changed from '{old_image}' to '{new_image}'")

        if changes:
            message = f"🔔 Project '{instance.title}' has been updated and requires approval:\n" + "\n".join(changes)
            for admin in get_admin_users():
                Notification.objects.create(user=admin, message=message)

@receiver(post_save, sender=FeasibilityStudy)
def notify_admin_feasibility_edited(sender, instance, created, **kwargs):
    if created:
        return  # Optionally notify on creation here if needed

    old_data = OLD_FEASIBILITY_CACHE.pop(instance.pk, None)
    if not old_data:
        return

    changes = []
    fields_to_check = [
        'current_revenue', 'funding_required', 'marketing_investment_percentage',
        'team_investment_percentage', 'expected_monthly_revenue', 'roi_period_months',
        'expected_profit_margin', 'growth_opportunity'
    ]

    for field in fields_to_check:
        old_value = old_data.get(field)
        new_value = getattr(instance, field)
        if old_value != new_value:
            changes.append(f"✏ Field '{field}' changed from '{old_value}' to '{new_value}'")

    if changes:
        project_title = instance.project.title if instance.project else "Unknown project"
        message = f"🔔 Feasibility study for project '{project_title}' has been updated:\n" + "\n".join(changes)
        for admin in get_admin_users():
            Notification.objects.create(user=admin, message=message)


#يلي فوق كلو وقت يعدل مشروغ





# 7- إشعار الأدمن عند تعديل دراسة الجدوى (بدون تعديل الحالة)



# 8- تحديث تقييم المستخدم عند إنشاء تقييم
@receiver(post_save, sender=Review)
def update_rating_on_review(sender, instance, created, **kwargs):
    if created:
        update_user_rating(instance.reviewed)
