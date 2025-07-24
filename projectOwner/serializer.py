from .models import Project, ProjectFile,FeasibilityStudy,ProjectOwner
from investor.models import Investor,InvestmentOffer
from rest_framework import serializers
from .utils import START_DATE

class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['file']


class FeasibilityStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeasibilityStudy
        exclude = ['project', 'created_at']  # سيتم ربطها لاحقاً بالمشروع تلقائياً


# serializers.py

class ProjectSerializer(serializers.ModelSerializer):
    files = ProjectFileSerializer(many=True, write_only=True, required=False)
    feasibility_study = FeasibilityStudySerializer(required=True)
    image = serializers.ImageField(required=False, allow_null=True)  # إضافة حقل الصورة

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'idea_summary', 'problem_solving',
            'category', 'readiness_level', 'files', 'feasibility_study', 'status', 'image'
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
    project_title = serializers.CharField(source='project.title', read_only=True)  # ⬅️ الجديد

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
            'project_title',  # ⬅️ الجديد
            'project',
        ]



class OfferStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentOffer
        fields = ['id', 'status']




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

from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from django.conf import settings

class ProjectDetailsSerializer(serializers.ModelSerializer):
    feasibility_study = FeasibilityStudySerializer(required=False)
    files = ProjectFileSerializer(source='projectfile_set', many=True, read_only=True)
    time_left_to_auto_close = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.user.full_name', read_only=True)
    image_url = serializers.SerializerMethodField()
    needs_review = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "status",
            "category", "readiness_level", "idea_summary",
            "problem_solving", "created_at", "updated_at",
            "feasibility_study", "files", "time_left_to_auto_close",
            "owner_name", "image_url", "needs_review"
        ]
        read_only_fields = ('status', 'files', 'owner_name', 'time_left_to_auto_close', 'image_url', 'needs_review')

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_time_left_to_auto_close(self, project):
        offers = InvestmentOffer.objects.filter(
            project=project,
            created_at__gte=START_DATE
        ).order_by('created_at')

        if not offers.exists():
            return "No investment offers yet"

        first_offer = offers.first()
        deadline = first_offer.created_at + timedelta(days=20)
        remaining = (deadline - timezone.now()).days

        return "Project should be closed" if remaining <= 0 else f"{remaining} day(s) left until auto-close"

    def get_needs_review(self, obj):
        return obj.status == "pending"

    def update(self, instance, validated_data):
        feasibility_data = validated_data.pop('feasibility_study', None)
        # جمع التعديلات المؤقتة
        pending = validated_data.copy()
        if feasibility_data:
            pending['feasibility_study'] = feasibility_data

        # حفظ التعديلات في حقل JSON مؤقت
        instance.pending_changes = pending
        # تغيير الحالة إلى pending
        instance.status = "pending"
        instance.save()
        return instance





class ProjectOwnerDashboardSerializer(serializers.Serializer):
    active_projects_count = serializers.IntegerField()
    total_funding_required = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_investors_connected = serializers.IntegerField()
    pending_offers = serializers.IntegerField()


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

# serializers.py
