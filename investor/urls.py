from django.urls import path
#from .views import (
 #   UserNegotiationConversationsView,
  #  NegotiationListCreateView,
   # mark_negotiation_messages_as_read,
    #RejectOfferView
#)
#from .views import AllProjectsListView
from .views import ConversationsListAPIView
from .views import ConversationDetailAPIView
from .views import InvestorOfferStatisticsAPIView

from .views import MarkMessagesReadAPIView,SendMessageAPIView,ProjectDetailView,ProjectFundingOnlyListView,CreateInvestmentOfferView,FilteredProjectList

urlpatterns = [
   # path('conversations/', UserNegotiationConversationsView.as_view(), name='user-conversations'),
    #path('negotiations/<int:offer_id>/', NegotiationListCreateView.as_view(), name='negotiation-list-create'),
    #path('negotiations/<int:offer_id>/mark-read/', mark_negotiation_messages_as_read, name='mark-negotiation-read'),   
    #path('offers/<int:offer_id>/reject/', RejectOfferView.as_view(), name='reject-offer'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),  # جديد
    path('conversations/', ConversationsListAPIView.as_view(), name='conversations-list'),
    path('conversations/<int:offer_id>/', ConversationDetailAPIView.as_view(), name='conversation-detail'),
    path('conversations/<int:offer_id>/send/', SendMessageAPIView.as_view(), name='send-message'),
    path('messages/<int:offer_id>/mark-read/', MarkMessagesReadAPIView.as_view(), name='mark-messages-read'),
    path('projects/all/view/',ProjectFundingOnlyListView.as_view(),name='all_project'),
    path('<int:project_id>/offers/create/', CreateInvestmentOfferView.as_view(), name='create-investment-offer'),
    path('projects/filter/', FilteredProjectList.as_view(), name='filtered-projects'),
    path('offer-statistics/', InvestorOfferStatisticsAPIView.as_view(), name='investor-offer-statistics'),

]
