# views.py
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Negotiation
from .serializer import NegotiationSerializer
from .models import InvestmentOffer

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q

from .models import InvestmentOffer, Negotiation
from .serializer import (
    NegotiationSerializer,
    NegotiationConversationSerializer
)

# عرض جميع المحادثات التي شارك فيها المستخدم
from django.db.models import Q, Exists, OuterRef

from django.db.models import Q, Exists, OuterRef
from .models import InvestmentOffer, Negotiation  # تأكد من استيراد الموديلات

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10 # عدد العناصر في كل صفحة
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserNegotiationConversationsView(generics.ListAPIView):
    serializer_class = NegotiationConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user

        negotiations_subquery = Negotiation.objects.filter(
            offer=OuterRef('pk')
        ).filter(
            Q(sender=user) |
            Q(offer__investor__user=user) |
            Q(offer__project__owner__user=user)
        )

        queryset = InvestmentOffer.objects.filter(
            Q(investor__user=user) | Q(project__owner__user=user)
        ).annotate(
            has_user_negotiations=Exists(negotiations_subquery)
        ).filter(
            has_user_negotiations=True
        ).select_related(
            'investor__user', 'project__owner__user'
        ).prefetch_related(
            'negotiations'
        ).order_by('-id')  # ← الترتيب هنا لحل المشكلة

        return queryset







# عرض وإنشاء رسائل لمحادثة معينة
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

        if offer.status == 'rejected':
            raise PermissionDenied("لا يمكن عرض المحادثة لعرض تم رفضه.")

        if user != offer.project.owner.user and user != offer.investor.user:
            raise PermissionDenied("غير مصرح لك بعرض هذه المحادثة.")

        return Negotiation.objects.filter(offer=offer).order_by('timestamp')

    def perform_create(self, serializer):
        offer = self.get_offer()
        user = self.request.user

        if offer.status == 'rejected':
            raise PermissionDenied("لا يمكن إرسال رسائل لعرض تم رفضه.")

        if user != offer.project.owner.user and user != offer.investor.user:
            raise PermissionDenied("غير مصرح لك بإرسال رسالة.")

        serializer.save(sender=user, offer=offer)



# تعليم الرسائل كمقروءة عند فتح المحادثة
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_negotiation_messages_as_read(request, offer_id):
    user = request.user
    try:
        offer = InvestmentOffer.objects.get(id=offer_id)
    except InvestmentOffer.DoesNotExist:
        return Response({'error': 'العرض غير موجود'}, status=404)

    if user != offer.project.owner.user and user != offer.investor.user:
        return Response({'error': 'غير مصرح لك'}, status=403)

    Negotiation.objects.filter(offer=offer, is_read=False).exclude(sender=user).update(is_read=True)
    return Response({'status': 'تم تعليم الرسائل كمقروءة'})



class RejectOfferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, offer_id):
        try:
            offer = InvestmentOffer.objects.select_related('project__owner__user').get(id=offer_id)
        except InvestmentOffer.DoesNotExist:
            return Response({"detail": "العرض غير موجود."}, status=status.HTTP_404_NOT_FOUND)

        if offer.project.owner.user != request.user:
            return Response({"detail": "غير مصرح لك برفض هذا العرض."}, status=status.HTTP_403_FORBIDDEN)

        offer.status = 'rejected'
        offer.save()

        return Response({"detail": "تم رفض العرض بنجاح."}, status=status.HTTP_200_OK)


from rest_framework import generics, permissions
from projectOwner.models import Project
from projectOwner.serializer import ProjectDetailsSerializer
from django.db.models import Q

class AllProjectsListView(generics.ListAPIView):
    serializer_class = ProjectDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_queryset(self):
        return Project.objects.filter(
            Q(status='active') | Q(status='under_negotiation')
        )


