from django.urls import path
from .views import CreateProjectView,MyProjectStatusView,MyProjectOffersView,FilteredOffersView,UpdateOfferStatusView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UpdateProjectOwnerProfileView
from .views import PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('projectowner/projects/add/', CreateProjectView.as_view(), name='add-project'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('my-projects/status/', MyProjectStatusView.as_view(), name='project-status-list'),
    path('my-projects/offers/', MyProjectOffersView.as_view(), name='my-project-offers'),
    path('my-projects/offers/filter/', FilteredOffersView.as_view(), name='filtered-offers'),
    path('offers/<int:offer_id>/update-status/', UpdateOfferStatusView.as_view(), name='update-offer-status'),
    path('project-owner/update-profile/', UpdateProjectOwnerProfileView.as_view(), name='update-project-owner-profile'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),


]
