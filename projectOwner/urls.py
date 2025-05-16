from django.urls import path
from .views import CreateProjectView,ProjectStatusView,ProjectOffersView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('projectowner/projects/add/', CreateProjectView.as_view(), name='add-project'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('view_status_all_project/',ProjectStatusView.as_view(),name='view_status_all_project'),
    path('asd/<int:project_id>/',ProjectOffersView.as_view(),name='asd')
]
