from django.urls import path
from .views import CreateProjectView,MyProjectOffersView,UpdateOfferStatusView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UpdateProjectOwnerProfileView
from .views import ProjectOwnerDashboardView
from .views import ProjectOwnerProjectsAPIView
from .views import FilteredOffersView, MyProjectDetailView
from .views import DetailedProjectAnalysisAPIView
from .views import ROIForecastAPIView
from .views import InvestmentDistributionAPIView
from .views import InvestorInterestAPIView
from .views import CapitalRecoveryHealthAPIView
from .views import ProjectStrengthsWeaknessesAPIView
from .views import ReadinessAlignmentAPIView
from .views import ImprovementSuggestionsAPIView

from .views import MyProjectsListView, MyProjectUpdateView,ValueForInvestmentAPIView
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
    path('project/<int:project_id>/detailed-analysis/', DetailedProjectAnalysisAPIView.as_view()),
    path('project/<int:project_id>/roi-forecast/', ROIForecastAPIView.as_view(), name='roi-forecast'),
    path('project/<int:project_id>/investment-distribution/', InvestmentDistributionAPIView.as_view()),
    path('project/<int:project_id>/investor-interest/', InvestorInterestAPIView.as_view()),
    path('project/<int:project_id>/capital-recovery-health/', CapitalRecoveryHealthAPIView.as_view()),
    path('project/<int:project_id>/ValueForInvestmentAPIView/', ValueForInvestmentAPIView.as_view()),
    path('project/<int:project_id>/strengths-weaknesses/', ProjectStrengthsWeaknessesAPIView.as_view()),
    path('project/<int:project_id>/readiness-alignment/', ReadinessAlignmentAPIView.as_view(), name='readiness-alignment'),
    path('project/<int:project_id>/improvement-suggestions/', ImprovementSuggestionsAPIView.as_view(), name='improvement-suggestions')



]
