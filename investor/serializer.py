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
    expected_monthly_revenue=serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "status",
            "category", "readiness_level", "idea_summary",
            "problem_solving", "created_at", 
            "funding_required","expected_monthly_revenue"
        ]
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
class ProjectMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'category', 'status', 'readiness_level']
#عرض كل المشاريع يلي قدم عليها المستثمر
class InvestmentOfferSerializer(serializers.ModelSerializer):
    project = ProjectMiniSerializer()  # ربط العرض بالمشروع المصغر

    class Meta:
        model = InvestmentOffer
        fields = [
            'id', 'amount', 'equity_percentage', 'additional_terms', 
            'status', 'created_at', 'updated_at', 'project'
        ]
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
        fields = ['id', 'full_name', 'email', 'role']

class InvestorSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()

    class Meta:
        model = Investor
        fields = ['id', 'user', 'rating_score', 'auto_rating_score', 'manual_rating_score']

class ProjectOwnerSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()

    class Meta:
        model = ProjectOwner
        fields = ['id', 'user', 'rating_score', 'auto_rating_score', 'manual_rating_score']
