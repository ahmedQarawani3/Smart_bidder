from rest_framework import serializers
from .models import Project, ProjectFile
from rest_framework import serializers
from .models import Project
class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['file']

class ProjectSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True, write_only=True, required=False)
    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'funding_goal', 'equity_percentage', 'duration_days', 'status', 'files']

    def create(self, validated_data):
        files_data = validated_data.pop('files', [])
        project = Project.objects.create(**validated_data)

        for file_data in files_data:
            ProjectFile.objects.create(project=project, **file_data)

        return project
    

class ProjectStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['title', 'status']

from rest_framework import serializers
from investor.models import InvestmentOffer

class InvestmentOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['amount', 'equity_percentage', 'status', 'created_at']
