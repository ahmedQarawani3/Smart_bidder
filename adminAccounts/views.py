from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .serializer import (
    AdminCreateInvestorSerializer,
    AdminCreateProjectOwnerSerializer
)
#انشاء مستثمر
class AdminCreateInvestorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admins can create investors.")

        serializer = AdminCreateInvestorSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Investor account created successfully by admin.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#انشاء صاحب مشروع
class AdminCreateProjectOwnerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admins can create project owners.")

        serializer = AdminCreateInvestorSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Project owner account created successfully by admin.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# user/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from .serializer import UserListSerializer, UpdateUserStatusSerializer

# user/views.py

from rest_framework import generics, permissions
#عرض المستخدمين مع فلاتر انو مستثمر ولا صاحب مشروع 
class ListAllUsersView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UserListSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role__in=['investor', 'owner'])

        role = self.request.query_params.get('role')
        if role in ['investor', 'owner']:
            queryset = queryset.filter(role=role)

        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() == 'true':
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() == 'false':
                queryset = queryset.filter(is_active=False)

        return queryset

#تعديل بيانات اليوزرس
class UpdateUserStatusView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = UpdateUserStatusSerializer
    queryset = User.objects.all()
    lookup_field = 'pk'

#حذف مستخدم
class DeleteUserView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    lookup_field = 'pk'
# user/views.py


from .serializer import UserDetailSerializer
#عرض تفاصيل اليوزرس مع تفعبل الحساب
class UserDetailAdminView(generics.RetrieveUpdateAPIView):  # ⬅️ يدعم GET + PATCH
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        is_active = request.data.get('is_active')

        if is_active is not None:
            user.is_active = is_active in ['true', 'True', True]
            user.save()
            return Response({'detail': f"User {'activated' if user.is_active else 'deactivated'} successfully."}, status=200)

        return Response({'error': 'Missing is_active field'}, status=400)

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from projectOwner.models import Project, FeasibilityStudy
from .serializer import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectUpdateSerializer,
)
#عرض المشاريع مع امكانيه الفلتره 
class ListProjectsView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        queryset = Project.objects.all().select_related('owner', 'feasibility_study')
        status_param = self.request.query_params.get('status')
        if status_param in ['active', 'under_negotiation', 'closed']:
            queryset = queryset.filter(status=status_param)
        return queryset

#عرض تفاصيل مشروع مع امكانيه التعديل عالحاله تبعو
class ProjectDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Project.objects.all().select_related('feasibility_study')
    serializer_class = ProjectDetailSerializer

    def patch(self, request, *args, **kwargs):
        project = self.get_object()
        feasibility = getattr(project, 'feasibility_study', None)

        # تحديث معلومات المشروع
        project_serializer = ProjectUpdateSerializer(project, data=request.data, partial=True)
        project_serializer.is_valid(raise_exception=True)
        project_serializer.save()

        # تحديث دراسة الجدوى إذا تم تمريرها
        feasibility_data = request.data.get('feasibility_study')
        if feasibility and feasibility_data:
            feasibility_serializer = FeasibilityStudySerializer(feasibility, data=feasibility_data, partial=True)
            feasibility_serializer.is_valid(raise_exception=True)
            feasibility_serializer.save()

        return Response({"detail": "Project and feasibility study updated successfully."})


#حذف مشروع 
class DeleteProjectFileView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Project.objects.all()
    lookup_field = 'pk'
#-------------------------------------------
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from investor.models import  InvestmentOffer, Negotiation
from .serializer import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectUpdateSerializer,
    FeasibilityStudySerializer,
    InvestmentOfferSerializer,
    InvestmentOfferDetailSerializer,
    NegotiationSerializer
)
#عرض العروض المقدمه للصاحب المشروع
class ListInvestmentOffersView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = InvestmentOfferSerializer
    queryset = InvestmentOffer.objects.all().select_related('investor', 'project')

#عرض التفاصيل تبع العرض مع الحذف او التعديل 
class InvestmentOfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = InvestmentOffer.objects.all()
    serializer_class = InvestmentOfferDetailSerializer
    lookup_field = 'pk'

#عرض المحادثه الخاصه بعرض معين
class OfferNegotiationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = NegotiationSerializer

    def get_queryset(self):
        offer_id = self.kwargs['offer_id']
        return Negotiation.objects.filter(offer_id=offer_id).select_related('sender')
    

from accounts.models import Complaint
from .serializer import ComplaintSerializer,ComplaintDetailSerializer

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from accounts.models import Complaint
from accounts.models import Notification
from .serializer import (
    ComplaintSerializer,
    ComplaintDetailSerializer,
    ComplaintUpdateSerializer,
    SubmitComplaintSerializer
)

# ✅ قائمة الشكاوى للمشرف
class ComplaintListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ComplaintSerializer
    queryset = Complaint.objects.all().select_related('complainant', 'defendant')

# ✅ عرض وتعديل وحذف شكوى للمشرف
class ComplaintDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Complaint.objects.all().select_related('complainant', 'defendant')
    serializer_class = ComplaintDetailSerializer
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        complaint = self.get_object()
        serializer = ComplaintUpdateSerializer(complaint, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # إشعار المستخدم المشتكي عند تحديث الحالة
        status_value = serializer.validated_data.get('status')
        if status_value:
            Notification.objects.create(
                user=complaint.complainant,
                message=f"تم تحديث حالة شكواك إلى: {status_value}"
            )

        return Response({'detail': 'Complaint updated successfully.'})

# ✅ تقديم شكوى من قبل مستثمر أو صاحب مشروع
class SubmitComplaintView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmitComplaintSerializer

    def get_serializer_context(self):
        return {"request": self.request}
