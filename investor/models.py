from django.db import models

# Create your models here.
from django.db import models
from accounts.models import User
from projectOwner.models import Project

class Investor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    commercial_register = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='investors/', blank=True, null=True)
    id_card_picture = models.ImageField(upload_to='investors/id_cards/', blank=True, null=True)

    def clean(self):
        if not self.commercial_register and not self.id_card_picture:
            raise ValidationError("If commercial register is not provided, a personal ID card picture is required.")

    def __str__(self):
        return f"Investor: {self.user.username}"


class InvestmentOffer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    equity_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    additional_terms = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



from django.db import models
from django.conf import settings

class Negotiation(models.Model):
    offer = models.ForeignKey(InvestmentOffer, on_delete=models.CASCADE, related_name="negotiations")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:30]}"
