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


class Project(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),

    )
    owner = models.ForeignKey(ProjectOwner, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    funding_goal = models.DecimalField(max_digits=12, decimal_places=2)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProjectFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(upload_to='project_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
