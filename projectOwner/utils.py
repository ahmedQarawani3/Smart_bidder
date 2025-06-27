from datetime import timedelta, datetime
from django.utils import timezone
from investor.models import InvestmentOffer
from accounts.utils import notify_user

# تاريخ بداية احتساب العروض (عدّل التاريخ حسب يوم بدء تفعيل النظام)
START_DATE = timezone.make_aware(datetime(2025, 3, 1, 0, 0, 0))

def auto_close_project_if_expired(project):
    offers = InvestmentOffer.objects.filter(
        project=project,
        created_at__gte=START_DATE
    ).order_by('created_at')

    if not offers.exists() or project.status != 'active':
        return

    first_offer_date = offers.first().created_at
    accepted_offer_exists = offers.filter(status='accepted').exists()

    if not accepted_offer_exists and timezone.now() > first_offer_date + timedelta(days=20):
        project.status = 'closed'
        project.save()

        # إشعار المستثمرين بأن المشروع اتسكر
        for offer in offers:
            investor_user = offer.investor.user
            message = f"The project '{project.title}' has been closed without accepting any investment offers."
            notify_user(investor_user, message)
