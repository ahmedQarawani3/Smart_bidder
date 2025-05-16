from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from django.shortcuts import get_object_or_404
from .models import Project, ProjectOwner
from .serializer import ProjectSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from investor.models import InvestmentOffer
from rest_framework import status
from rest_framework import generics, permissions
from .models import Project
from .serializer import ProjectStatusSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import ProjectOwner, Project
from investor.models import InvestmentOffer  # حسب مكان الملف
from .serializer import InvestmentOfferSerializer
class CreateProjectView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise AuthenticationFailed('User is not authenticated')

        owner = get_object_or_404(ProjectOwner, user=self.request.user)
        serializer.save(owner=owner)
from rest_framework.permissions import IsAuthenticated

    

#عرض المشاريع الخاصه بي
class MyProjectStatusView(generics.ListAPIView):
    serializer_class = ProjectStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # نحصل على كائن ProjectOwner المرتبط بالمستخدم
        project_owner = ProjectOwner.objects.get(user=self.request.user)
        return Project.objects.filter(owner=project_owner)

#عرض العروض المقدمه لصاحب المشروع
class MyProjectOffersView(generics.ListAPIView):
    serializer_class = InvestmentOfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # الحصول على صاحب المشروع المرتبط بالمستخدم الحالي
        project_owner = ProjectOwner.objects.get(user=self.request.user)
        # الحصول على المشاريع التي يملكها
        owner_projects = Project.objects.filter(owner=project_owner)
        # جلب كل العروض المرتبطة بهذه المشاريع
        return InvestmentOffer.objects.filter(project__in=owner_projects)
#فلتره العروض 
# projectOwner/views.py
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProjectOwner, Project
from investor.models import InvestmentOffer
from .serializer import InvestmentOfferSerializer

class FilteredOffersView(generics.ListAPIView):
    serializer_class = InvestmentOfferSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    # يمكن فلترة حسب القيمة أو النسبة
    filterset_fields = ['amount', 'equity_percentage', 'status']
    
    # يمكن الترتيب حسب الزمن أو القيمة
    ordering_fields = ['amount', 'equity_percentage', 'created_at']

    def get_queryset(self):
        project_owner = ProjectOwner.objects.get(user=self.request.user)
        owner_projects = Project.objects.filter(owner=project_owner)
        return InvestmentOffer.objects.filter(project__in=owner_projects)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from investor.models import InvestmentOffer
from .serializer import OfferStatusUpdateSerializer
#قبول ورفض عرض استثماري
class UpdateOfferStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, offer_id):
        try:
            offer = InvestmentOffer.objects.get(id=offer_id)
        except InvestmentOffer.DoesNotExist:
            return Response({'error': 'Offer not found'}, status=404)

        # تحقق من أن المستخدم هو صاحب المشروع
        if request.user != offer.project.owner.user:
            return Response({'error': 'Unauthorized'}, status=403)

        new_status = request.data.get('status')
        if new_status not in ['Accepted', 'Rejected']:
            return Response({'error': 'Invalid status'}, status=400)

        if new_status == 'Accepted':
            # غلق المشروع
            project = offer.project
            project.status = 'Closed'
            project.save()

            # رفض باقي العروض
            InvestmentOffer.objects.filter(project=project).exclude(id=offer.id).update(status='Rejected')

        offer.status = new_status
        offer.save()

        return Response({'message': f'Offer has been {new_status.lower()}'}, status=200)
