from django.urls import path
from .views import AdminCreateInvestorView, AdminCreateProjectOwnerView
from .views import ListAllUsersView, UpdateUserStatusView, DeleteUserView,UserDetailAdminView
from .views import (
    ListProjectsView,
    ProjectDetailAdminView,
    DeleteProjectFileView,
    ListInvestmentOffersView,
    InvestmentOfferDetailView,
    OfferNegotiationsView
)
urlpatterns = [
    path('create-investor/', AdminCreateInvestorView.as_view(), name='admin-create-investor'),
    path('create-owner/', AdminCreateProjectOwnerView.as_view(), name='admin-create-owner'),
    path('users/All/', ListAllUsersView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/update/', UpdateUserStatusView.as_view(), name='admin-user-update'),
    path('users/<int:pk>/delete/', DeleteUserView.as_view(), name='admin-user-delete'),
    path('users/<int:pk>/details/', UserDetailAdminView.as_view(), name='admin-user-detail'),
    path('projects/', ListProjectsView.as_view(), name='admin-list-projects'),
    path('projects/<int:pk>/', ProjectDetailAdminView.as_view(), name='admin-project-detail'),
    path('projects/<int:pk>/delete-file/', DeleteProjectFileView.as_view(), name='admin-project-file-delete'),
    path('offers/', ListInvestmentOffersView.as_view(), name='admin-list-investment-offers'),
    path('offers/<int:pk>/', InvestmentOfferDetailView.as_view(), name='admin-investment-offer-detail'),
    path('offers/<int:offer_id>/negotiations/', OfferNegotiationsView.as_view(), name='admin-offer-negotiations'),

]
