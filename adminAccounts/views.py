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

        serializer = AdminCreateProjectOwnerSerializer(data=request.data, context={'request': request})
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
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404

class OfferNegotiationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = NegotiationSerializer

    def get_queryset(self):
        offer_id = self.kwargs['offer_id']
        offer = get_object_or_404(InvestmentOffer, id=offer_id)
        return Negotiation.objects.filter(offer=offer).select_related(
            'sender',
            'offer__investor__user',
            'offer__project__owner__user'
        )





    

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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated  # أو AllowAny حسب حاجتك

from django.contrib.auth import get_user_model
from projectOwner.models import Project
from investor.models import InvestmentOffer

User = get_user_model()

class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]  # غيرها لـ AllowAny لو بدك بدون توثيق

    def get(self, request):
        total_users = User.objects.count()
        active_projects = Project.objects.filter(status='active').count()
        total_investments = InvestmentOffer.objects.filter(status='accepted').count()

        total_projects_approved = Project.objects.exclude(status='pending').count()
        projects_closed = Project.objects.filter(status='closed').count()
        success_rate = 0

        if total_projects_approved > 0:
            success_rate = round((projects_closed / total_projects_approved) * 100, 2)  # بالنسبة %

        data = {
            "total_users": total_users,
            "active_projects": active_projects,
            "total_investments": total_investments,
            "success_rate_percent": success_rate
        }

        return Response(data)
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from projectOwner.models import Project
from projectOwner.serializer import ProjectDetailsSerializer  # لازم يكون عندك سيريلزر للتفاصيل
from projectOwner.utils import notify_user  # فرضاً دالة لإرسال الإشعارات

class AdminApproveProjectUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, status='pending')
        except Project.DoesNotExist:
            return Response({"detail": "No pending project found with this ID."}, status=status.HTTP_404_NOT_FOUND)

        # هنا تفترض ان الموافقة تعني تغيير الحالة إلى active (أو حسب منطقك)
        project.status = 'active'
        project.save()

        # إرسال إشعار لصاحب المشروع (اختياري)
        notify_user(project.owner.user, f"تمت الموافقة على تعديل مشروعك '{project.title}'.")

        return Response({"detail": "Project update approved."}, status=status.HTTP_200_OK)


class AdminRejectProjectUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, status='pending')
        except Project.DoesNotExist:
            return Response({"detail": "No pending project found with this ID."}, status=status.HTTP_404_NOT_FOUND)

        # رفض التعديل: نرجع المشروع لحالته السابقة أو حالة خاصة (مثلاً 'active' أو غيرها)
        # إذا عندك نسخة سابقة محفوظة للتراجع، تحتاج منطق إضافي، هنا بس نرجع لـ active بشكل مبسط:
        project.status = 'active'  # أو يمكن 'needs_revision' أو حسب ما تحدد
        project.save()

        # إرسال إشعار لصاحب المشروع (اختياري)
        notify_user(project.owner.user, f"تم رفض تعديل مشروعك '{project.title}'. الرجاء تعديل البيانات وإعادة المحاولة.")

        return Response({"detail": "Project update rejected."}, status=status.HTTP_200_OK)


from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class AdminProjectReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        if request.user.role != "admin":
            return Response({"detail": "You are not authorized."}, status=403)

        action = request.data.get("action")  # "accept" or "reject"
        if action not in ["accept", "reject"]:
            return Response({"detail": "Invalid action."}, status=400)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=404)

        if action == "accept":
            project.status = "active"
            project.save()
            notify_user(project.owner.user, f"✅ تم قبول تعديلات مشروعك: {project.title}")
        elif action == "reject":
            notify_user(project.owner.user, f"❌ تم رفض تعديلات مشروعك: {project.title}. الرجاء مراجعته.")

        return Response({"detail": f"Project {action}ed successfully."})

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import FeasibilityStudy, Project, Notification
from .serializer import (
    FeasibilityStudySerializer,
    ProjectSerializer,
    AdminApprovalSerializer,
)
import requests
from django.contrib.auth import get_user_model

User = get_user_model()


class FeasibilityStudyViewSet(viewsets.ModelViewSet):
    queryset = FeasibilityStudy.objects.all()
    serializer_class = FeasibilityStudySerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        self.send_to_ai(instance)

    def send_to_ai(self, instance):
        project = instance.project

        data = {
            "title": project.title,
            "description": project.description,
            "idea_summary": project.idea_summary,
            "problem_solving": project.problem_solving,
            "category": project.category,
            "readiness_level": project.readiness_level,
            "funding_required": float(instance.funding_required),
            "current_revenue": float(instance.current_revenue) if instance.current_revenue else 0.0,
            "expected_monthly_revenue": instance.expected_monthly_revenue,
            "expected_profit_margin": instance.expected_profit_margin,
            "roi_period_months": instance.roi_period_months,
            "growth_opportunity": instance.growth_opportunity,
        }

        try:
            response = requests.post("http://localhost:8005/evaluate-project", json=data)
            result = response.json()

            instance.ai_score = result.get("score")
            instance.save(update_fields=["ai_score"])

            message = f"""
📊 تقييم AI جديد لمشروع: {project.title}
✅ النتيجة: {result.get("score")}
💬 التعليق: {result.get("message")}
"""

            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    message=message.strip()
                )

        except Exception as e:
            print("🔴 فشل تقييم AI:", e)


# ✅ API ليقوم الأدمن بالموافقة أو الرفض
class AdminProjectApprovalAPIView(APIView):
    def post(self, request, project_id):
        serializer = AdminApprovalSerializer(data=request.data)
        if serializer.is_valid():
            approved = serializer.validated_data['approved']
            try:
                project = Project.objects.get(id=project_id)
                project.status = "active" if approved else "closed"
                project.save()

                message = f"تم {'الموافقة' if approved else 'رفض'} المشروع: {project.title}"
                Notification.objects.create(
                    user=project.owner.user,
                    message=message
                )

                return Response({"detail": message}, status=200)

            except Project.DoesNotExist:
                return Response({"error": "المشروع غير موجود"}, status=404)

        return Response(serializer.errors, status=400)
