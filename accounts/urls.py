from django.urls import path
from .views import ProjectOwnerRegisterView
from .views import LoginView

urlpatterns = [
    path('register/project-owner', ProjectOwnerRegisterView.as_view(), name='project_owner_register'),
    path('login/', LoginView.as_view(), name='login'),

]
