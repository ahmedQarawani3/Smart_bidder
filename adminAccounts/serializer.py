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


from rest_framework import serializers
from projectOwner.models import Project, FeasibilityStudy

#-------------------------------------------------------------------------------

class ProjectOwnerBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']


class ProjectListSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'status', 'category', 'readiness_level', 'created_at', 'owner']

    def get_owner(self, obj):
        return ProjectOwnerBasicSerializer(obj.owner.user).data


class FeasibilityStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeasibilityStudy
        fields = '__all__'


class ProjectDetailSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    feasibility_study = FeasibilityStudySerializer(read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def get_owner(self, obj):
        return ProjectOwnerBasicSerializer(obj.owner.user).data


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'description', 'status', 'idea_summary', 'problem_solving', 'category', 'readiness_level']

#----------------------------------------------------------------------
from investor.models import InvestmentOffer,Negotiation
class InvestmentOfferSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source='project.title', read_only=True)
    investor_name = serializers.SerializerMethodField()
    project_owner_name = serializers.SerializerMethodField()

    class Meta:
        model = InvestmentOffer
        fields = [
            'id',  'project_title',
             'investor_name',
            'project_owner_name',
            'amount', 'equity_percentage',
            'status', 'created_at'
        ]

    def get_investor_name(self, obj):
        return obj.investor.user.full_name if obj.investor and obj.investor.user else None

    def get_project_owner_name(self, obj):
        try:
            return obj.project.owner.user.full_name
        except:
            return None




class InvestmentOfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = '__all__'


from rest_framework import serializers
from investor.models import Negotiation

class NegotiationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    sender_role = serializers.SerializerMethodField()  # ✅

    class Meta:
        model = Negotiation
        fields = ['id', 'sender_name', 'sender_role', 'message', 'timestamp', 'is_read']

    def get_sender_role(self, obj):
        user = obj.sender
        if Investor.objects.filter(user=user).exists():
            return 'investor'
        elif ProjectOwner.objects.filter(user=user).exists():
            return 'owner'
        else:
            return 'unknown'





# admin_project_management/serializers.py

from rest_framework import serializers
from accounts.models import Complaint
from accounts.models import User

from rest_framework import serializers
from accounts.models import Complaint, User

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'username']

class ComplaintSerializer(serializers.ModelSerializer):
    complainant = UserMiniSerializer(read_only=True)
    defendant = UserMiniSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'

class ComplaintDetailSerializer(serializers.ModelSerializer):
    complainant = UserMiniSerializer(read_only=True)
    defendant = UserMiniSerializer(read_only=True)

    class Meta:
        model = Complaint
        fields = '__all__'

class ComplaintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['status']

# ✅ يستخدمه المستخدم عند تقديم شكوى
class SubmitComplaintSerializer(serializers.ModelSerializer):
    defendant_username = serializers.CharField(write_only=True)  # ✅ نستخدم username بدلاً من full_name

    class Meta:
        model = Complaint
        fields = ['description', 'defendant_username']

    def validate_defendant_username(self, value):
        try:
            user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("لا يوجد مستخدم بهذا الاسم.")
        return user

    def create(self, validated_data):
        defendant_user = validated_data.pop('defendant_username')  # ✅ من النوع User
        complainant_user = self.context['request'].user
        return Complaint.objects.create(
            complainant=complainant_user,
            defendant=defendant_user,
            **validated_data
        )


from rest_framework import serializers
from .models import Project, FeasibilityStudy

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class FeasibilityStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeasibilityStudy
        fields = '__all__'
        read_only_fields = ['ai_score']  # لأنه سيتم توليده تلقائيًا

class AdminApprovalSerializer(serializers.Serializer):
    approved = serializers.BooleanField()
