from rest_framework import serializers
from .models import Project, ProjectFile,FeasibilityStudy
from rest_framework import serializers
from .models import Project
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
    feasibility_study = FeasibilityStudySerializer(required=False)

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'idea_summary', 'problem_solving',
            'category', 'readiness_level', 'files', 'feasibility_study','status'
        ]

    def validate(self, data):
        readiness = data.get('readiness_level')
        feasibility_data = data.get('feasibility_study')

        # إذا المشروع "فكرة" فلا حاجة لإدخال بيانات الجدوى
        if readiness == 'idea' and feasibility_data:
            raise serializers.ValidationError("No feasibility study is required for idea-level projects.")
        
        # إذا المشروع أكثر من فكرة ولم تُرفق الجدوى
        if readiness in ['prototype', 'existing'] and not feasibility_data:
            raise serializers.ValidationError("Feasibility study is required for prototype or existing projects.")
        
        return data

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        feasibility_data = validated_data.pop('feasibility_study', None)

        project = Project.objects.create(**validated_data)

        for file_data in files_data:
            ProjectFile.objects.create(project=project, **file_data)

        if feasibility_data:
            FeasibilityStudy.objects.create(project=project, **feasibility_data)

        return project


#عرض المشاريع الخاصه بي
from rest_framework import serializers
from .models import Project

class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'status', 'created_at', 'updated_at']


#عرض العروض المقدمه لصاحب المشروع
from rest_framework import serializers
from investor.models import InvestmentOffer  # حسب مكان الملف عندك

class InvestmentOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['id', 'amount', 'equity_percentage', 'additional_terms', 'status', 'created_at']

#فلتره العروض حسب معايير معينه
from rest_framework import serializers
from investor.models import InvestmentOffer

class InvestmentOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['id', 'amount', 'equity_percentage', 'additional_terms', 'status', 'created_at']

from rest_framework import serializers
from investor.models import InvestmentOffer
#قبول ورفض عرض استثماري

class OfferStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['id', 'status']
