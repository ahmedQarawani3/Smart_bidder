from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('investor', 'Investor'),
        ('owner', 'Project Owner'),
    )
    full_name=models.CharField(max_length=150, unique=True)  
    username = models.CharField(max_length=150, unique=True)  
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    language_preference = models.CharField(max_length=10, default='ar')
    phone_number = models.CharField(max_length=20)  
    created_at = models.DateTimeField(default=timezone.now)  
    updated_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)  # 👈 المستخدم غير مفعل حتى موافقة الأدمن

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role', 'phone_number']

    def __str__(self):
        return f"{self.username} ({self.role})"


class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username


class Complaint(models.Model):
    complainant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints_made')
    defendant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints_received')
    description = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
