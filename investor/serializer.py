from rest_framework import serializers
from .models import Negotiation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name']

class NegotiationLastMessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    from_me = serializers.SerializerMethodField()

    class Meta:
        model = Negotiation
        fields = ['id', 'message', 'timestamp', 'is_read', 'sender', 'from_me']

    def get_from_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False





from rest_framework import serializers
from .models import Negotiation



from rest_framework import serializers
from .models import Negotiation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name']

class NegotiationSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    from_me = serializers.SerializerMethodField()

    class Meta:
        model = Negotiation
        fields = ['id', 'offer', 'sender', 'message', 'timestamp', 'is_read', 'from_me']

    def get_from_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False


from projectOwner.models import Project
#عرض المشاريغ للمستثمر بدون تفاضيل
class ProjectFundingSerializer(serializers.ModelSerializer):
    funding_required = serializers.SerializerMethodField()
    expected_monthly_revenue = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "status",
            "category", "readiness_level", "idea_summary",
            "problem_solving", "created_at", 
            "funding_required", "expected_monthly_revenue",
            "image_url",
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                return obj.image.url
        return None

    def get_funding_required(self, obj):
        if hasattr(obj, 'feasibility_study') and obj.feasibility_study:
            return obj.feasibility_study.funding_required
        return None

    def get_expected_monthly_revenue(self, obj):
        if hasattr(obj, 'feasibility_study') and obj.feasibility_study:
            return obj.feasibility_study.expected_monthly_revenue
        return None
from rest_framework import serializers
from .models import InvestmentOffer

class InvestmentOfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['amount', 'equity_percentage', 'additional_terms']

#عرض من عند صفحه العروض من فوق تبع كم عرض مقدك وهدول الشغلات

class OfferStatisticsSerializer(serializers.Serializer):
    total_offers = serializers.IntegerField()
    pending_offers = serializers.IntegerField()
    accepted_offers = serializers.IntegerField()
    rejected_offers = serializers.IntegerField()
    total_invested_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
#عرض كل المشاريع يلي قدم عليها المستثمر
from rest_framework import serializers

class ProjectMiniSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'title', 'category', 'status', 'readiness_level', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            else:
                return obj.image.url
        return None

#عرض كل المشاريع يلي قدم عليها المستثمر
class InvestmentOfferSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source='investor.user.full_name', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    investor_profile_picture = serializers.SerializerMethodField()
    project_image = serializers.SerializerMethodField()

    class Meta:
        model = InvestmentOffer
        fields = [
            'id',
            'amount',
            'equity_percentage',
            'additional_terms',
            'status',
            'created_at',
            'investor_name',
            'investor_profile_picture',
            'project_title',
            'project',
            'project_image',
        ]

    def get_investor_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.investor.profile_picture:
            url = obj.investor.profile_picture.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_project_image(self, obj):
        request = self.context.get('request')
        if obj.project.image:
            url = obj.project.image.url
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return None


from rest_framework import serializers
from accounts.models import User
from .models import Investor
class InvestorUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone_number = serializers.CharField(source='user.phone_number', required=False)

    class Meta:
        model = Investor
        fields = [
            'full_name',
            'email',
            'phone_number',
            'company_name',
            'commercial_register',
            'profile_picture',
            'id_card_picture',
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
# accounts/serializers.py أو حسب مكانك

from rest_framework import serializers
from investor.models import Investor
from projectOwner.models import ProjectOwner
from accounts.models import User  # حسب مكان موديل المستخدم

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name', 'role']  # ❌ بدون الإيميل


class InvestorSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Investor
        fields = ['id', 'user', 'profile_picture', 'rating_score']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture:
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None





class ProjectOwnerSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()
    profile_picture_url = serializers.SerializerMethodField()
    final_rating = serializers.FloatField( read_only=True)
    bio = serializers.CharField()

    class Meta:
        model = ProjectOwner
        fields = ['id', 'user', 'final_rating', 'profile_picture_url', 'bio']


    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            # صيغة رابط كامل للصورة
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None

