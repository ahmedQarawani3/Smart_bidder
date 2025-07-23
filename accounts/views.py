from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import ProjectOwnerRegisterSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import LoginSerializer
from .serializer import InvestorRegisterSerializer
from rest_framework import generics, permissions
from .models import Notification
from .serializer import NotificationSerializer
class ProjectOwnerRegisterView(APIView):
    def post(self, request):
        serializer = ProjectOwnerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Project owner registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InvestorRegisterView(APIView):
    def post(self, request):
        serializer = InvestorRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'investor registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate



class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not user.check_password(current_password):
            return Response({"detail": "Current password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"detail": "New password and confirmation do not match."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


#لعرض كل الإشعارات
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

#لتحديد إشعار كمقروء
class MarkNotificationAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({'detail': 'Notification marked as read'})
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

#لتحديد كل الإشعارات كمقروءة
class MarkAllNotificationsAsReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'All notifications marked as read'})

#لحذف إشعار
class DeleteNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.delete()
            return Response({'detail': 'Notification deleted'})
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializer import PasswordResetRequestSerializer


# إرسال رابط إعادة التعيين
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'A new password has been sent to your email.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from accounts.models import User
from projectOwner.models import Project,ProjectOwner
from investor.models import Investor, InvestmentOffer

class UserContextAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role
        context = {
            "username": user.username,
            "full_name": user.full_name,
            "language": user.language_preference,
        }

        if role == "owner":
            try:
                owner = ProjectOwner.objects.get(user=user)
                projects = Project.objects.filter(owner=owner)
                context['projects'] = [
                    {
                        "title": p.title,
                        "description": p.description,
                        "status": p.status,
                        "category": p.category,
                        "readiness": p.readiness_level
                    }
                    for p in projects
                ]
            except ProjectOwner.DoesNotExist:
                context['projects'] = []

        elif role == "investor":
            try:
                investor = Investor.objects.get(user=user)
                offers = InvestmentOffer.objects.filter(investor=investor)
                context['offers'] = [
                    {
                        "project": o.project.title,
                        "amount": float(o.amount),
                        "equity": float(o.equity_percentage),
                        "status": o.status
                    }
                    for o in offers
                ]
            except Investor.DoesNotExist:
                context['offers'] = []

        elif role == "admin":
            context["info"] = "أنت مدير، لديك صلاحيات شاملة."

        return Response({
            "user_id": user.id,
            "role": role,
            "context": context
        })
    
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Review
from .serializer import ReviewSerializer

class SubmitInvestorReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        try:
            offer = InvestmentOffer.objects.get(id=offer_id)
        except InvestmentOffer.DoesNotExist:
            return Response({'detail': 'Offer not found.'}, status=status.HTTP_404_NOT_FOUND)

        # ✅ التحقق من أن المستخدم الحالي هو صاحب المشروع المرتبط بالعرض
        if offer.project.owner.user != request.user:
            return Response({'detail': 'You are not authorized to review this offer.'}, status=status.HTTP_403_FORBIDDEN)

        # ✅ التحقق إذا سبق وتم تقييم المستثمر
        reviewed_user = offer.investor.user
        if Review.objects.filter(reviewer=request.user, reviewed=reviewed_user).exists():
            return Response({'detail': 'You already reviewed this investor.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reviewer=request.user, reviewed=reviewed_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



from functools import reduce
from django.db import models

from rest_framework import generics, permissions
from accounts.models import Notification
from accounts.serializer import NotificationSerializer

from functools import reduce
from django.db.models import Q
from rest_framework import generics, permissions
from accounts.models import Notification

class ImportantAdminNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'admin':
            return Notification.objects.none()
        
        keywords = [
            "Project created",
            "Project updated",
            "new account created",
            "score reached",
            
        ]
        
        query = reduce(lambda q1, q2: q1 | q2,
                       [Q(message__icontains=kw) for kw in keywords])
        
        qs = Notification.objects.filter(user=user).filter(query).order_by('-created_at')
        return qs

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from projectOwner.models import Project
from .serializer import ProjectEvaluationSerializer
import httpx
import traceback
from decimal import Decimal

class EvaluateProjectAIView(APIView):
    def get(self, request, pk):
        try:
            project = Project.objects.get(id=pk)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectEvaluationSerializer(project)
        project_data = serializer.data

        feasibility_data = project_data.pop('feasibility_study', {})
        for key, value in feasibility_data.items():
            if isinstance(value, Decimal):
                value = float(value)
            project_data[key] = value

        print("🟢 Final AI Payload:", project_data)

        try:
            ai_response = httpx.post(
                "http://127.0.0.1:8005/evaluate-project",
                json=project_data,
                timeout=30.0
            )

            if ai_response.status_code == 200:
                result = ai_response.json()
                return Response({
                    "score": result.get("score"),
                    "message": result.get("message")
                }, status=status.HTTP_200_OK)

            return Response({
                "error": "AI service error",
                "details": ai_response.text
            }, status=ai_response.status_code)

        except Exception as e:
            print("🔥 EXCEPTION:", str(e))
            traceback.print_exc()
            return Response({
                "error": "Internal Server Error",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from .serializer import ProjectEvaluationSerializer
from projectOwner.serializer import ProjectSerializer
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from accounts.models import Notification
from django.contrib.auth import get_user_model
import httpx

User = get_user_model()



class CreateProjectView(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        owner = get_object_or_404(ProjectOwner, user=self.request.user)
        project = serializer.save(owner=owner, status='pending')

        # الـ AI evaluation مفصول كما طلبت، لا تعدل عليه
        self.ai_score = None
        self.ai_comment = None

        feasibility = getattr(project, "feasibility_study", None)
        if not feasibility:
            return

        ai_payload = {
            "title": project.title,
            "description": project.description,
            "idea_summary": project.idea_summary,
            "problem_solving": project.problem_solving,
            "category": project.category,
            "readiness_level": project.readiness_level,
            "funding_required": float(feasibility.funding_required),
            "current_revenue": float(feasibility.current_revenue or 0),
            "expected_monthly_revenue": feasibility.expected_monthly_revenue,
            "expected_profit_margin": feasibility.expected_profit_margin,
            "roi_period_months": feasibility.roi_period_months,
            "growth_opportunity": feasibility.growth_opportunity,
        }

        try:
            ai_res = httpx.post("http://127.0.0.1:8005/evaluate-project", json=ai_payload, timeout=30.0)

            if ai_res.status_code == 200:
                result = ai_res.json()
                self.ai_score = result.get("score")
                self.ai_comment = result.get("message")

                # إشعار للأدمن فقط، دون حفظ score/comment في المشروع
                if self.ai_score is not None and self.ai_comment:
                    admins = User.objects.filter(role='admin')
                    for admin in admins:
                        Notification.objects.create(
                            user=admin,
                            message=f"مشروع جديد '{project.title}' تم تقييمه بسكور {self.ai_score} وملاحظة: {self.ai_comment}"
                        )

        except Exception as e:
            print("⚠ AI Evaluation Error:", str(e))

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if hasattr(self, "ai_score"):
            response.data["ai_score"] = self.ai_score
        if hasattr(self, "ai_comment"):
            response.data["ai_comment"] = self.ai_comment

        return response



# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import User
from .serializer import UserReviewSerializer
from .models import Notification

class PendingUserDetailView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_active=False)
            serializer = UserReviewSerializer(user, context={'request': request})
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found or already active."}, status=404)



class ApproveUserView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_active=False)
            user.is_active = True
            user.save()

            Notification.objects.create(
                user=user,
                message="Your account has been approved by the admin."
            )

            return Response({"message": "User approved successfully."})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


class RejectUserView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id, is_active=False)

            Notification.objects.create(
                user=user,
                message="Your account has been rejected by the admin."
            )

            user.delete()
            return Response({"message": "User rejected and deleted successfully."})
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
