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

