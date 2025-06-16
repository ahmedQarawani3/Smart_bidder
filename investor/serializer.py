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
