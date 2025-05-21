from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser,JSONParser
from django.shortcuts import get_object_or_404
from .serializer import ProjectSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import generics, permissions
from .serializer import ProjectStatusSerializer
from .serializer import ProjectOwnerUpdateSerializer
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import ProjectOwner, Project
from .serializer import InvestmentOfferSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from investor.models import InvestmentOffer
from .serializer import OfferStatusUpdateSerializer

class CreateProjectView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        owner = get_object_or_404(ProjectOwner, user=self.request.user)
        serializer.save(owner=owner)


#عرض المشاريع الخاصه بي
class MyProjectStatusView(generics.ListAPIView):
    serializer_class = ProjectStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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



class UpdateProjectOwnerProfileView(generics.UpdateAPIView):
    queryset = ProjectOwner.objects.all()
    serializer_class = ProjectOwnerUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.project_owner_profile
