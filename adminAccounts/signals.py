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
from django.db.models.signals import post_save
from projectOwner.models import FeasibilityStudy
from django.dispatch import receiver
import requests
from accounts.models import Notification, User  # يفترض لديك موديل إشعارات

@receiver(post_save, sender=FeasibilityStudy)
def evaluate_with_ai(sender, instance, created, **kwargs):
    if created:
        project = instance.project

        data = {
            "title": project.title,
            "description": project.description,
            "idea_summary": project.idea_summary,
            "problem_solving": project.problem_solving,
            "category": project.category,
            "readiness_level": project.readiness_level,
            "funding_required": float(instance.funding_required),
            "current_revenue": float(instance.current_revenue) if instance.current_revenue else 0.0,
            "expected_monthly_revenue": instance.expected_monthly_revenue,
            "expected_profit_margin": instance.expected_profit_margin,
            "roi_period_months": instance.roi_period_months,
            "growth_opportunity": instance.growth_opportunity,
        }

        try:
            response = requests.post("http://localhost:8005/evaluate-project", json=data)
            result = response.json()
            instance.ai_score = result.get("score")
            instance.save(update_fields=["ai_score"])

            # إرسال إشعار للأدمن
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    message=f"📊 تقييم AI جديد لمشروع: {project.title} - النتيجة: {result.get('score')} / التعليق: {result.get('message')}"
                )

        except Exception as e:
            print("🔴 AI Evaluation Failed:", str(e))
