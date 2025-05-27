from .models import Project, ProjectFile,FeasibilityStudy
from rest_framework import serializers
from investor.models import InvestmentOffer

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





class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'status', 'created_at', 'updated_at']


class InvestmentOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['id', 'amount', 'equity_percentage', 'additional_terms', 'status', 'created_at']



class OfferStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['id', 'status']

# serializers.py
from rest_framework import serializers
from .models import ProjectOwner

from rest_framework import serializers
from .models import ProjectOwner

# serializers.py

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


class FeasibilityStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeasibilityStudy
        fields = [
            "current_revenue",
            "funding_required",
            "marketing_investment_percentage",
            "team_investment_percentage",
            "expected_monthly_revenue",
            "roi_period_months",
            "expected_profit_margin",
            "growth_opportunity",
            "created_at",
        ]


class ProjectDetailsSerializer(serializers.ModelSerializer):
    feasibility_study = FeasibilityStudySerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "status",
            "category",
            "readiness_level",
            "idea_summary",
            "problem_solving",
            "created_at",
            "updated_at",
            "feasibility_study",
        ]
