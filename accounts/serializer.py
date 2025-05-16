from .models import  User
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from projectOwner.models import ProjectOwner
class ProjectOwnerRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(max_length=20)
    bio = serializers.CharField(allow_blank=True)
    company_name = serializers.CharField(max_length=255)
    profile_picture = serializers.ImageField(required=False)
    id_card_picture = serializers.ImageField(required=False)
    terms_agreed = serializers.CharField(required=True)

    class Meta:
        model = ProjectOwner
        fields = [
            'username', 'email', 'password', 'phone_number',
            'bio', 'company_name', 'profile_picture',
            'id_card_picture', 'terms_agreed'
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
                    is_active=False
                )

                owner = ProjectOwner.objects.create(
                    user=user,
                    bio=validated_data.get('bio', ''),
                    company_name=validated_data.get('company_name', ''),
                    profile_picture=validated_data.get('profile_picture'),
                    id_card_picture=validated_data.get('id_card_picture'),
                    terms_agreed=validated_data.get('terms_agreed', '')
                )
                return owner
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})




class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

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

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }
