from rest_framework import serializers
from django.db import transaction
from accounts.models import User
from investor.models import Investor
from projectOwner.models import ProjectOwner

# ✅ Register Investor - Admin
class AdminCreateInvestorSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    company_name = serializers.CharField(required=False, allow_blank=True)
    commercial_register = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False)
    id_card_picture = serializers.ImageField(required=False)
    terms_agreed = serializers.CharField()

    class Meta:
        model = Investor
        fields = [
            'username', 'email', 'password', 'phone_number',
            'company_name', 'commercial_register',
            'profile_picture', 'id_card_picture',
            'terms_agreed', 'full_name'
        ]

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data['full_name'],
                phone_number=validated_data['phone_number'],
                role='investor',
                is_active=True
            )
            investor = Investor.objects.create(
                user=user,
                company_name=validated_data.get('company_name', ''),
                commercial_register=validated_data.get('commercial_register', ''),
                phone_number=validated_data['phone_number'],
                profile_picture=validated_data.get('profile_picture'),
                id_card_picture=validated_data.get('id_card_picture'),
                created_by=self.context['request'].user

            )
            return investor

# ✅ Register Project Owner - Admin
class AdminCreateProjectOwnerSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False)
    id_card_picture = serializers.ImageField(required=False)
    terms_agreed = serializers.CharField()

    class Meta:
        model = ProjectOwner
        fields = [
            'username', 'email', 'password', 'full_name', 'phone_number',
            'bio', 'profile_picture', 'id_card_picture', 'terms_agreed'
        ]

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                full_name=validated_data['full_name'],
                phone_number=validated_data['phone_number'],
                role='owner',
                is_active=True
            )
            owner = ProjectOwner.objects.create(
                user=user,
                bio=validated_data.get('bio', ''),
                profile_picture=validated_data.get('profile_picture'),
                id_card_picture=validated_data.get('id_card_picture'),
                terms_agreed=validated_data['terms_agreed'],
                created_by=self.context['request'].user

            )
            return owner
# user/serializers.py

from rest_framework import serializers
from projectOwner.models import ProjectOwner
from investor.models import Investor

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'phone_number', 'role', 'is_active', 'created_at']


class InvestorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investor
        exclude = ['user']


class ProjectOwnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectOwner
        # نعرض كل الحقول بدون user لأنه موجود في الـ User
        fields = ['bio', 'profile_picture', 'id_card_picture', 'terms_agreed', 'created_by']


class UserDetailSerializer(serializers.ModelSerializer):
    investor_data = serializers.SerializerMethodField()
    owner_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'full_name', 'phone_number',
            'role', 'is_active', 'created_at', 'updated_at',
            'investor_data', 'owner_data'
        ]

    def get_investor_data(self, obj):
        if obj.role == 'investor':
            try:
                return InvestorDetailSerializer(obj.investor).data
            except Investor.DoesNotExist:
                return None
        return None

    def get_owner_data(self, obj):
        if obj.role == 'owner':
            try:
                return ProjectOwnerDetailSerializer(obj.project_owner_profile).data
            except ProjectOwner.DoesNotExist:
                return None
        return None


class UpdateUserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active', 'email', 'phone_number', 'full_name']
