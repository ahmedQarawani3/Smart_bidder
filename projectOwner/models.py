from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
from django.db import models
from accounts.models import User
User = get_user_model()

class ProjectOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='project_owner_profile')
    bio = models.TextField(blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='owners/', blank=True, null=True)
    id_card_picture = models.ImageField(upload_to='owners/id_cards/', blank=True, null=True)  
    terms_agreed = models.TextField(blank=True)  

    def __str__(self):
        return f"Project Owner: {self.user.username}"


# models.py
class Project(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
    )

    CATEGORY_CHOICES = (
        ('medical', 'Medical'),
        ('general_trade', 'General Trade'),
        ('construction', 'Construction'),
        ('business', 'Business'),
        ('other', 'Other'),
    )


    READINESS_CHOICES = (
        ('idea', 'Idea'),
        ('prototype', 'Prototype'),
        ('existing', 'Existing Project'),
    )

    owner = models.ForeignKey(ProjectOwner, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    idea_summary = models.TextField(null=True, blank=True)         
    problem_solving = models.TextField(null=True, blank=True)      # 11111المشكلة التي يحلها
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)#111111
    readiness_level = models.CharField(max_length=50, choices=READINESS_CHOICES, null=True, blank=True)#11111
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeasibilityStudy(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='feasibility_study')
    
    current_stage = models.CharField(max_length=255)  # مثل: فكرة، نموذج أولي، مشروع قائم
    current_revenue = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # الإيرادات الحالية بالدولار
    funding_required = models.DecimalField(max_digits=12, decimal_places=2)  # التمويل المطلوب بالدولار

    marketing_investment_percentage = models.PositiveIntegerField()  # نسبة للتسويق
    team_investment_percentage = models.PositiveIntegerField()     # نسبة للفريق

    expected_monthly_revenue = models.CharField(max_length=255)  # الإيرادات الشهرية المتوقعة
    roi_period_months = models.PositiveIntegerField()  # عدد الأشهر لاسترداد رأس المال
    expected_profit_margin = models.CharField(max_length=255)  # هامش الربح المتوقع
    market_size = models.CharField(max_length=255)  # حجم السوق المتوقع
    growth_opportunity = models.TextField()  # وصف لفرصة النمو
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feasibility for Project {self.project.title}"




class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to='project_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

