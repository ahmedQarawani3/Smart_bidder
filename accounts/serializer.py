from .models import  User
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from projectOwner.models import ProjectOwner
from investor.models import Investor

class ProjectOwnerRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=20)
    bio = serializers.CharField(allow_blank=True)
    profile_picture = serializers.ImageField(required=False)
    id_card_picture = serializers.ImageField(required=False)
    terms_agreed = serializers.CharField(required=True)
    full_name=serializers.CharField(required=True)
    class Meta:
        model = ProjectOwner
        fields = [
            'username', 'email', 'password', 'phone_number',
            'bio',  'profile_picture',
            'id_card_picture', 'terms_agreed','full_name'
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    password=validated_data['password'],
                    role='owner',
                    phone_number=validated_data['phone_number'],
                    full_name=validated_data['full_name'],
                    is_active=False
                )

                owner = ProjectOwner.objects.create(
                    user=user,
                    bio=validated_data.get('bio', ''),
                    profile_picture=validated_data.get('profile_picture'),
                    id_card_picture=validated_data.get('id_card_picture'),
                    terms_agreed=validated_data.get('terms_agreed', '')
                )
                return owner
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

class InvestorRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=20)
    company_name = serializers.CharField(allow_blank=True, required=False)
    commercial_register = serializers.CharField(allow_blank=True, required=False)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    id_card_picture = serializers.ImageField(required=False, allow_null=True)
    terms_agreed = serializers.CharField(required=True)
    full_name = serializers.CharField(required=True)

    class Meta:
        model = Investor
        fields = [
            'username', 'email', 'password', 'phone_number',
            'company_name', 'commercial_register', 'profile_picture',
            'id_card_picture', 'terms_agreed', 'full_name'
        ]

    def create(self, validated_data):
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=validated_data['username'],
                    email=validated_data['email'],
                    password=validated_data['password'],
                    role='investor',
                    phone_number=validated_data['phone_number'],
                    full_name=validated_data['full_name'],
                    is_active=False
                )

                investor = Investor.objects.create(
                    user=user,
                    company_name=validated_data.get('company_name', ''),
                    commercial_register=validated_data.get('commercial_register', ''),
                    phone_number=validated_data['phone_number'],
                    profile_picture=validated_data.get('profile_picture'),
                    id_card_picture=validated_data.get('id_card_picture'),
                )

                return investor
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})



from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField(read_only=True)  # ما في داعي نخليه required من المستخدم

    def validate(self, data):
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        if user is None:
            raise serializers.ValidationError("The username or password is incorrect.")
        if not user.is_active:
            raise serializers.ValidationError("The account is not activated.")

        refresh = RefreshToken.for_user(user)

        # افترضنا أن حقل role موجود ضمن user model
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'role': user.role  # هون جبنا الدور من حساب المستخدم
        }

from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from django.conf import settings
import string
import random

User = get_user_model()

def generate_random_password(length=8):
    # Generate a random password with letters and digits
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.strip().lower()
        if not User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value

    def save(self):
        email = self.validated_data["email"].strip().lower()
        user = User.objects.filter(email__iexact=email).first()

        if user:
            # Generate new random password
            new_password = generate_random_password()
            # Set new password
            user.set_password(new_password)
            user.save()

            # Send the new password via email
            send_mail(
                "Your New Password",
                f"Your password has been reset. Your new password is:\n\n{new_password}\n\nPlease change it after logging in.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )



from projectOwner.models import FeasibilityStudy,Project

from rest_framework import serializers
from .models import Review
class FeasibilityStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeasibilityStudy
        fields = [
            'id',
            "current_revenue",
            "funding_required",
            "marketing_investment_percentage",
            "team_investment_percentage",
            "expected_monthly_revenue",
            "roi_period_months",
            "expected_profit_margin",
            "growth_opportunity",
        ]
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewed', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'reviewer', 'reviewed', 'created_at']

class ProjectEvaluationSerializer(serializers.ModelSerializer):
    feasibility_study = FeasibilityStudySerializer()

    class Meta:
        model = Project
        fields = [
            'title', 'description', 'idea_summary',
            'problem_solving', 'category', 'readiness_level',
            'feasibility_study'
        ]

# accounts/serializers.py
from rest_framework import serializers
from .models import User

from rest_framework import serializers
class ProjectOwnerProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    id_card_picture = serializers.SerializerMethodField()

    class Meta:
        model = ProjectOwner
        fields = ['bio', 'profile_picture', 'id_card_picture', 'terms_agreed']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None

    def get_id_card_picture(self, obj):
        request = self.context.get('request')
        if obj.id_card_picture:
            return request.build_absolute_uri(obj.id_card_picture.url) if request else obj.id_card_picture.url
        return None


class InvestorProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    id_card_picture = serializers.SerializerMethodField()
    commercial_register_picture = serializers.SerializerMethodField()

    class Meta:
        model = Investor
        fields = ['company_name', 'commercial_register', 'phone_number', 'profile_picture', 'id_card_picture', 'commercial_register_picture']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None

    def get_id_card_picture(self, obj):
        request = self.context.get('request')
        if obj.id_card_picture:
            return request.build_absolute_uri(obj.id_card_picture.url) if request else obj.id_card_picture.url
        return None

    def get_commercial_register_picture(self, obj):
        request = self.context.get('request')
        if obj.commercial_register_picture:
            return request.build_absolute_uri(obj.commercial_register_picture.url) if request else obj.commercial_register_picture.url
        return None


class UserReviewSerializer(serializers.ModelSerializer):
    project_owner_profile = serializers.SerializerMethodField()
    investor_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'phone_number', 'role', 'created_at', 'is_active', 'project_owner_profile', 'investor_profile']

    def get_project_owner_profile(self, obj):
        if obj.role == 'owner' and hasattr(obj, 'project_owner_profile'):
            return ProjectOwnerProfileSerializer(obj.project_owner_profile, context=self.context).data
        return None

    def get_investor_profile(self, obj):
        if obj.role == 'investor' and hasattr(obj, 'investor'):
            return InvestorProfileSerializer(obj.investor, context=self.context).data
        return None

# serializers.py
# serializers.py
from rest_framework import serializers

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'username', 'email', 'phone_number', 'role', 'language_preference', 'created_at', 'is_active']

class InvestorDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)
    
    class Meta:
        model = Investor
        fields = [
            'user', 'company_name', 'commercial_register', 'phone_number',
            'profile_picture', 'id_card_picture', 'commercial_register_picture',
            'created_by_name', 'created_at'
        ]

class ProjectOwnerDetailSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()
    
    class Meta:
        model = ProjectOwner
        fields = [
            'user', 'bio', 'profile_picture', 'id_card_picture', 
            'terms_agreed'
        ]

class NewUserDetailSerializer(serializers.ModelSerializer):
    investor_details = InvestorDetailSerializer(source='investor', read_only=True, allow_null=True)
    project_owner_details = ProjectOwnerDetailSerializer(source='project_owner_profile', read_only=True, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'username', 'email', 'phone_number', 'role', 
            'language_preference', 'created_at', 'is_active',
            'investor_details', 'project_owner_details'
        ]