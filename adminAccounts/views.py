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
