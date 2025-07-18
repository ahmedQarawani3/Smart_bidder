from django.urls import path
from .views import ProjectOwnerRegisterView,InvestorRegisterView
from .views import LoginView
from .views import ChangePasswordView
from .views import (
    NotificationListView,
    MarkNotificationAsReadView,
    MarkAllNotificationsAsReadView,
    DeleteNotificationView
)
from .views import PasswordResetRequestView
from .views import UserContextAPIView
from .views import SubmitInvestorReviewAPIView


urlpatterns = [
    path('register/project-owner/', ProjectOwnerRegisterView.as_view(), name='project_owner_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('register/investor/',InvestorRegisterView.as_view(),name='investor_register'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/mark-read/', MarkNotificationAsReadView.as_view(), name='notification-mark-read'),
    path('notifications/mark-all-read/', MarkAllNotificationsAsReadView.as_view(), name='notification-mark-all-read'),
    path('notifications/<int:pk>/delete/', DeleteNotificationView.as_view(), name='notification-delete'),
    path('reset-password/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('chat-context/', UserContextAPIView.as_view(), name='user-context'),
    path('offers/<int:offer_id>/review/', SubmitInvestorReviewAPIView.as_view(), name='submit-review'),

]
