from .models import Project, ProjectFile,FeasibilityStudy
from rest_framework import serializers
from investor.models import InvestmentOffer
from rest_framework import serializers
from .models import ProjectOwner
from rest_framework import serializers
from .models import ProjectOwner
class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['file']


class FeasibilityStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeasibilityStudy
        exclude = ['project', 'created_at']  # سيتم ربطها لاحقاً بالمشروع تلقائياً


class ProjectSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True, write_only=True, required=False)
    feasibility_study = FeasibilityStudySerializer(required=True)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'idea_summary', 'problem_solving',
            'category', 'readiness_level', 'files', 'feasibility_study', 'status'
        ]

    def validate(self, data):
        feasibility_data = data.get('feasibility_study', {})
        readiness_level = data.get('readiness_level')

        required_fields = [
            'funding_required',
            'marketing_investment_percentage',
            'team_investment_percentage',
            'expected_monthly_revenue',
            'roi_period_months',
            'expected_profit_margin',
            'growth_opportunity',
        ]

        if not feasibility_data:
            raise serializers.ValidationError({'feasibility_study': 'This field is required.'})

        for field in required_fields:
            if not feasibility_data.get(field):
                raise serializers.ValidationError({
                    'feasibility_study': f'The field {field} is required.'
                })

        if readiness_level != 'idea':
            if feasibility_data.get('current_revenue') in [None, '']:
                raise serializers.ValidationError({
                    'feasibility_study': 'The field current_revenue is required because the project is not just an idea.'
                })

        return data

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        feasibility_data = validated_data.pop('feasibility_study')

        project = Project.objects.create(**validated_data)

        for file_data in files_data:
            ProjectFile.objects.create(project=project, **file_data)

        FeasibilityStudy.objects.create(project=project, **feasibility_data)

        return project


#هاد تمام عرض العروض المقدمه لصاحب المشروع مع فلاره
class InvestmentOfferSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source='investor.user.full_name', read_only=True)  

    class Meta:

        model = InvestmentOffer
        fields = [
            'id',
            'amount',
            'equity_percentage',
            'additional_terms',
            'status',
            'created_at',
            'investor',         
            'investor_name',   
            'project'
        ]

class OfferStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['id', 'status']


from rest_framework import serializers
from .models import ProjectOwner, Project, FeasibilityStudy

class ProjectOwnerUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', required=False)
    email = serializers.EmailField(source='user.email', required=False)
    phone_number = serializers.CharField(source='user.phone_number', required=False)

    class Meta:
        model = ProjectOwner
        fields = [
            'full_name',
            'email',
            'phone_number',
            'bio',
            'profile_picture',
            'id_card_picture'
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


# serializers.py
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


class ProjectDetailsSerializer(serializers.ModelSerializer):
    feasibility_study = FeasibilityStudySerializer()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "status",
            "category", "readiness_level", "idea_summary",
            "problem_solving", "created_at", "updated_at",
            "feasibility_study",
        ]



# serializers.py

from rest_framework import serializers

class ProjectOwnerDashboardSerializer(serializers.Serializer):
    active_projects_count = serializers.IntegerField()
    total_funding_required = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_investors_connected = serializers.IntegerField()
    pending_offers = serializers.IntegerField()
# projects/serializers.py
from rest_framework import serializers
from .models import Project, FeasibilityStudy
from investor.models import Investor
from investor.models import InvestmentOffer

class ProjectListSerializer(serializers.ModelSerializer):
    funding_required = serializers.SerializerMethodField()
    funding_achieved = serializers.SerializerMethodField()
    investor_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'status', 'category', 'readiness_level',
            'funding_required', 'funding_achieved', 'investor_count'
        ]

    def get_funding_required(self, obj):
        return getattr(obj.feasibility_study, 'funding_required', 0)

    def get_funding_achieved(self, obj):
        return InvestmentOffer.objects.filter(project=obj, status='accepted') \
            .aggregate(total=models.Sum('amount'))['total'] or 0

    def get_investor_count(self, obj):
        return InvestmentOffer.objects.filter(project=obj, status='accepted') \
            .values('investor').distinct().count()

from rest_framework import serializers
from .models import Project, FeasibilityStudy

class FeasibilityStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeasibilityStudy
        exclude = ['project', 'created_at']

class ProjectWithFeasibilitySerializer(serializers.ModelSerializer):
    feasibility_study = FeasibilityStudySerializer(required=False)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def update(self, instance, validated_data):
        feasibility_data = validated_data.pop('feasibility_study', None)

        # تحديث بيانات المشروع
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # تحديث جزئي لبيانات دراسة الجدوى
        if feasibility_data:
            feasibility_instance = instance.feasibility_study
            for attr, value in feasibility_data.items():
                setattr(feasibility_instance, attr, value)
            feasibility_instance.save()

        return instance

