from django.urls import path
from .views import CreateProjectView,MyProjectOffersView,UpdateOfferStatusView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UpdateProjectOwnerProfileView
from .views import ProjectOwnerDashboardView
from .views import ProjectOwnerProjectsAPIView
from .views import FilteredOffersView, MyProjectDetailView
from .views import ProjectStatsAPIView

from .views import MyProjectsListView, MyProjectUpdateView
urlpatterns = [
    path('projectowner/projects/add/', CreateProjectView.as_view(), name='add-project'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('my-projects/offers/', MyProjectOffersView.as_view(), name='my-project-offers'),
    path('offers/<int:offer_id>/update-status/', UpdateOfferStatusView.as_view(), name='update-offer-status'),
    path('project-owner/update-profile/', UpdateProjectOwnerProfileView.as_view(), name='update-project-owner-profile'),
    path("my-projects/", MyProjectsListView.as_view(), name="my-projects"),#11
    path("my-projects/<int:project_id>/", MyProjectUpdateView.as_view(), name="my-project-update"),#11
    path('dashboard/', ProjectOwnerDashboardView.as_view(), name='projectowner-dashboard'),#11
    path('my-projects/', ProjectOwnerProjectsAPIView.as_view(), name='my-projects'),
    path('project-owner/offers/', FilteredOffersView.as_view(), name='filtered-investment-offers'),#11
    path('my-projectss/<int:project_id>/', MyProjectDetailView.as_view(), name='my-project-detail'),
    path('api/project-stats/', ProjectStatsAPIView.as_view(), name='project-stats'),



]
