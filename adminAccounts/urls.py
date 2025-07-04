from django.urls import path
from .views import AdminCreateInvestorView, AdminCreateProjectOwnerView
from .views import ListAllUsersView, UpdateUserStatusView, DeleteUserView,UserDetailAdminView

urlpatterns = [
    path('create-investor/', AdminCreateInvestorView.as_view(), name='admin-create-investor'),
    path('create-owner/', AdminCreateProjectOwnerView.as_view(), name='admin-create-owner'),
    path('users/All/', ListAllUsersView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/update/', UpdateUserStatusView.as_view(), name='admin-user-update'),
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='admin-user-delete'),
    path('users/<int:pk>/details/', UserDetailAdminView.as_view(), name='admin-user-detail'),

]
