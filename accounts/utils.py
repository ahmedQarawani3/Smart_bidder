from .models import Notification

def notify_user(user, message):
    Notification.objects.create(user=user, message=message)

def notify_users(users, message):
    for user in users:
        Notification.objects.create(user=user, message=message)
from django.db.models import Avg
from .models import  Review
from projectOwner.models import Project
def calculate_auto_rating_project_owner(project_owner):
    total_projects = Project.objects.filter(owner=project_owner).count()
    projects_sold = Project.objects.filter(owner=project_owner, status='closed').count()
    rating = (total_projects * 0.7) + (projects_sold * 0.3)
    return rating

def calculate_auto_rating_investor(investor):
    from investor.models import InvestmentOffer  # حسب مكان الموديل عندك
    total_invested = InvestmentOffer.objects.filter(investor=investor, status='accepted').count()
    return total_invested * 1.0

def calculate_manual_rating(user):
    reviews = Review.objects.filter(reviewed=user)
    if not reviews.exists():
        return 0
    return reviews.aggregate(Avg('rating'))['rating__avg']

def update_user_rating(user):
    if hasattr(user, 'project_owner_profile'):
        owner = user.project_owner_profile
        auto = calculate_auto_rating_project_owner(owner)
        manual = calculate_manual_rating(user)
        owner.auto_rating_score = auto
        owner.manual_rating_score = manual
        owner.rating_score = (auto * 0.6) + (manual * 0.4)
        owner.save(update_fields=['auto_rating_score', 'manual_rating_score', 'rating_score'])
    elif hasattr(user, 'investor'):
        investor = user.investor
        auto = calculate_auto_rating_investor(investor)
        manual = calculate_manual_rating(user)
        investor.auto_rating_score = auto
        investor.manual_rating_score = manual
        investor.rating_score = (auto * 0.6) + (manual * 0.4)
        investor.save(update_fields=['auto_rating_score', 'manual_rating_score', 'rating_score'])
