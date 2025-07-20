from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from django.shortcuts import get_object_or_404
from .serializer import ProjectSerializer
from rest_framework.exceptions import AuthenticationFailed
from .serializer import ProjectOwnerUpdateSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializer import InvestmentOfferSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from investor.models import InvestmentOffer
from .serializer import OfferStatusUpdateSerializer
from .serializer import ProjectDetailsSerializer
from rest_framework.generics import RetrieveUpdateAPIView
from .serializer import FeasibilityStudySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, permissions
from .models import Project,FeasibilityStudy,ProjectOwner
from  investor.models import  InvestmentOffer
# projects/views.py
from rest_framework import generics, permissions
from .models import Project
from .serializer import ProjectListSerializer
from django.db.models import Q
from accounts.utils import notify_user

from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import Sum
from .serializer import ProjectOwnerDashboardSerializer
#انشاء مشروع 
class CreateProjectView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        owner = get_object_or_404(ProjectOwner, user=self.request.user)
        serializer.save(owner=owner, status='pending')  # ✅ نجبر المشروع يبدأ كـ pending


#عرض العروض المقدمه لصاحب المشروع

class MyProjectOffersView(generics.ListAPIView):
    serializer_class = InvestmentOfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            project_owner = ProjectOwner.objects.get(user=user)
        except ProjectOwner.DoesNotExist:
            # المستخدم ليس صاحب مشروع، ما يعرض له أي عروض
            return InvestmentOffer.objects.none()

        # استعلام يعرض فقط عروض الاستثمار التي تخص مشاريع صاحب المشروع الحالي
        return InvestmentOffer.objects.filter(project__owner=project_owner)



# قبول عرض استثماري فقط (رفض العروض الأخرى تلقائيًا)

class UpdateOfferStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, offer_id):
        try:
            offer = InvestmentOffer.objects.select_related('project__owner__user').get(id=offer_id)
        except InvestmentOffer.DoesNotExist:
            return Response({'error': 'Offer not found.'}, status=404)

        if request.user != offer.project.owner.user:
            return Response({'error': 'You are not authorized to accept this offer.'}, status=403)

        new_status = request.data.get('status')
        if new_status != 'Accepted':
            return Response({'error': 'This endpoint is only for accepting offers.'}, status=400)

        project = offer.project

        if project.status.lower() == 'closed':
            return Response({'error': 'The project is closed and cannot accept new offers.'}, status=400)

        if offer.status == 'accepted':
            return Response({'error': 'This offer has already been accepted.'}, status=400)

        project.status = 'Closed'
        project.save()

        InvestmentOffer.objects.filter(project=project).exclude(id=offer.id).update(status='rejected')

        offer.status = 'accepted'
        offer.save()

        return Response({'message': 'Offer accepted successfully.'}, status=200)


#update and get profile
class UpdateProjectOwnerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProjectOwnerUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.project_owner_profile

#عرض المشاريع الخاصه بي
class MyProjectsListView(generics.ListAPIView):
    serializer_class = ProjectDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(owner__user=self.request.user)

#تعديل مشروع خاص بي 
class MyProjectUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, project_id):
        try:
            project_owner = ProjectOwner.objects.get(user=request.user)
            project = Project.objects.get(id=project_id, owner=project_owner)
        except ProjectOwner.DoesNotExist:
            return Response({"detail": "You are not registered as a project owner."}, status=status.HTTP_403_FORBIDDEN)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectDetailsSerializer(instance=project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # ✅ رفض العروض إذا كانت موجودة
            offers = InvestmentOffer.objects.filter(project=project, status='pending')

            for offer in offers:
                offer.status = 'rejected'
                offer.save()
                print(f"Rejected offer ID: {offer.id} for investor {offer.investor.user}")

                message = f"Your offer for '{project.title}' has been rejected due to project updates by the owner."
                notify_user(offer.investor.user, message)


            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#عرض active_projects_count وtotal_funding_required وtotal_investors_connected وpending_offers
class ProjectOwnerDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            project_owner = ProjectOwner.objects.get(user=request.user)
        except ProjectOwner.DoesNotExist:
            return Response({"detail": "Project owner not found."}, status=404)

        projects = Project.objects.filter(owner=project_owner)

        active_projects = projects.filter(status='active')
        active_projects_count = active_projects.count()

        total_funding = FeasibilityStudy.objects.filter(project__in=active_projects)\
            .aggregate(total=Sum('funding_required'))['total'] or 0

        total_investors = InvestmentOffer.objects.filter(project__in=projects)\
            .values('investor').distinct().count()

        pending_offers = InvestmentOffer.objects.filter(project__in=projects, status='pending').count()

        data = {
            "active_projects_count": active_projects_count,
            "total_funding_required": total_funding,
            "total_investors_connected": total_investors,
            "pending_offers": pending_offers
        }

        serializer = ProjectOwnerDashboardSerializer(data)
        return Response(serializer.data)


class ProjectOwnerProjectsAPIView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        search = self.request.query_params.get('search', '').strip().lower()
        status_filter = self.request.query_params.get('status')

        queryset = Project.objects.filter(owner__user=user)

        if search:
            queryset = queryset.annotate(
                title_f=Coalesce('title', Value('')),
                description_f=Coalesce('description', Value('')),
                idea_summary_f=Coalesce('idea_summary', Value('')),
                problem_solving_f=Coalesce('problem_solving', Value('')),
            ).filter(
                Q(title_f__icontains=search) |
                Q(description_f__icontains=search) |
                Q(idea_summary_f__icontains=search) |
                Q(problem_solving_f__icontains=search)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')




from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter
from .serializer import InvestmentOfferSerializer

# فلتر مخصص حسب طلبك
class InvestmentOfferFilter(FilterSet):
    search = CharFilter(method='filter_search', label='Search offers')
    amount = NumberFilter(field_name="amount")
    equity_percentage = NumberFilter(field_name="equity_percentage")
    status = CharFilter(field_name="status")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            project__title__icontains=value
        )

    class Meta:
        model = InvestmentOffer
        fields = ['search', 'amount', 'equity_percentage', 'status']


class FilteredOffersView(generics.ListAPIView):
    serializer_class = InvestmentOfferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = InvestmentOfferFilter
    ordering_fields = ['created_at', 'amount']

    def get_queryset(self):
        project_owner = ProjectOwner.objects.get(user=self.request.user)
        owner_projects = Project.objects.filter(owner=project_owner)
        return InvestmentOffer.objects.filter(project__in=owner_projects)



from .serializer import ProjectDetailsSerializer
from .utils import auto_close_project_if_expired

class MyProjectDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        try:
            project_owner = ProjectOwner.objects.get(user=request.user)
            project = Project.objects.get(id=project_id, owner=project_owner)
        except ProjectOwner.DoesNotExist:
            return Response({"detail": "You are not registered as a project owner."}, status=403)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        # تحقق من إغلاق المشروع تلقائيًا عند عرض التفاصيل
        auto_close_project_if_expired(project)

        serializer = ProjectDetailsSerializer(project)
        return Response(serializer.data)
# your_app/views.py


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .data_analysis import calculate_detailed_project_analysis,calculate_roi_forecast,calculate_investment_distribution

class DetailedProjectAnalysisAPIView(APIView):
    def get(self, request, project_id):
        result = calculate_detailed_project_analysis(project_id)
        return Response(result)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FeasibilityStudy
 

from rest_framework.views import APIView
from rest_framework.response import Response

class ROIForecastAPIView(APIView):
    def get(self, request, project_id):
        result = calculate_roi_forecast(project_id)
        return Response(result)

from rest_framework.views import APIView
from rest_framework.response import Response

class InvestmentDistributionAPIView(APIView):
    def get(self, request, project_id):
        result = calculate_investment_distribution(project_id)
        return Response(result)
from rest_framework.views import APIView
from rest_framework.response import Response
from .data_analysis import calculate_investor_interest

class InvestorInterestAPIView(APIView):
    def get(self, request, project_id):
        result = calculate_investor_interest(project_id)
        return Response(result)

from rest_framework.views import APIView
from rest_framework.response import Response
from .data_analysis import analyze_capital_recovery

class CapitalRecoveryHealthAPIView(APIView):
    def get(self, request, project_id):
        result = analyze_capital_recovery(project_id)
        return Response(result)
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .data_analysis import get_strengths_and_weaknesses

class ProjectStrengthsWeaknessesAPIView(APIView):
    def get(self, request, project_id):
        result = get_strengths_and_weaknesses(project_id)
        return Response(result)
from rest_framework.views import APIView
from rest_framework.response import Response
from .data_analysis import analyze_readiness_alignment

class ReadinessAlignmentAPIView(APIView):
    def get(self, request, project_id):
        result = analyze_readiness_alignment(project_id)
        return Response(result)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from django.views import View
from .models import FeasibilityStudy
from .data_analysis import cost_to_revenue_analysis  # افترضنا الدالة موجودة في هذا الملف

class CostToRevenueAnalysisView(View):
    def get(self, request, project_id):
        try:
            fs = FeasibilityStudy.objects.get(project_id=project_id)
        except FeasibilityStudy.DoesNotExist:
            return JsonResponse({"error": "No feasibility study found for this project."}, status=404)
        
        result = cost_to_revenue_analysis(fs)
        return JsonResponse(result)

    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from investor.models import Investor
from projectOwner.models import ProjectOwner
from investor.serializer import InvestorSerializer, ProjectOwnerSerializer 
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

class TopProjectOwnersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        owners = ProjectOwner.objects.filter(rating_score__gt=0).order_by('-rating_score')[:5]
        serializer = ProjectOwnerSerializer(owners, many=True, context={'request': request})
        return Response(serializer.data)
