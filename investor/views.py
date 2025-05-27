from django.shortcuts import render

# Create your views here.
# views.py

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Negotiation
from .serializer import NegotiationSerializer
from .models import InvestmentOffer
class NegotiationListCreateView(generics.ListCreateAPIView):
    serializer_class = NegotiationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_offer(self):
        offer_id = self.kwargs['offer_id']
        try:
            offer = InvestmentOffer.objects.select_related('project__owner__user', 'investor__user').get(id=offer_id)
        except InvestmentOffer.DoesNotExist:
            raise PermissionDenied("العرض غير موجود.")
        return offer

    def get_queryset(self):
        offer = self.get_offer()
        user = self.request.user

        if user != offer.project.owner.user and user != offer.investor.user:
            raise PermissionDenied("غير مصرح لك بعرض هذه المحادثة.")

        return Negotiation.objects.filter(offer=offer).order_by('timestamp')

    def perform_create(self, serializer):
        offer = self.get_offer()
        user = self.request.user

        if user != offer.project.owner.user and user != offer.investor.user:
            raise PermissionDenied("غير مصرح لك بإرسال رسالة.")

        serializer.save(sender=user, offer=offer)

