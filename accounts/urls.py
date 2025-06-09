from django.urls import path
from .views import ProjectOwnerRegisterView,InvestorRegisterView
from .views import LoginView
from .views import ChangePasswordView

urlpatterns = [
    path('register/project-owner', ProjectOwnerRegisterView.as_view(), name='project_owner_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('register/investor',InvestorRegisterView.as_view(),name='investor_register')

]
