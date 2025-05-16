from django.urls import path
from .views import NegotiationListCreateView

urlpatterns = [
    path('offers/<int:offer_id>/negotiations/', NegotiationListCreateView.as_view(), name='negotiation'),

]
