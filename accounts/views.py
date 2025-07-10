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