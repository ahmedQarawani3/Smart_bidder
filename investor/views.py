from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max, Q
from .models import Negotiation
from django.contrib.auth import get_user_model
from projectOwner.models import Project
User = get_user_model()

from django.db.models import Q, Max, Count, Case, When, BooleanField

class ConversationsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'investor':
            negotiations = Negotiation.objects.filter(investor=user)
        elif user.role == 'owner':
            negotiations = Negotiation.objects.filter(offer__project__owner__user=user)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

        last_msgs = negotiations.values('offer', 'investor').annotate(last_timestamp=Max('timestamp'))

        conversations = []
        for item in last_msgs:
            offer_id = item['offer']
            investor_id = item['investor']
            last_time = item['last_timestamp']
            last_msg = negotiations.filter(offer_id=offer_id, investor_id=investor_id, timestamp=last_time).first()

            offer = last_msg.offer

            if user == last_msg.sender:
                if user.role == 'investor':
                    other_user = offer.project.owner.user
                else:
                    other_user = last_msg.investor
            else:
                other_user = last_msg.sender

            unread_exists = negotiations.filter(
                offer=offer_id,
                investor=investor_id,
                is_read=False
            ).exclude(sender=user).exists()

            conversations.append({
                'offer_id': offer_id,
                'investor_id': investor_id,
                'other_user_id': other_user.id,
                'other_user_full_name': other_user.full_name,
                'last_message': last_msg.message,
                'last_message_time': last_msg.timestamp,
                'is_read': not unread_exists,
            })

        conversations.sort(key=lambda x: x['last_message_time'], reverse=True)

        return Response(conversations)






# views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Negotiation

class MarkMessagesReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        user = request.user
        # تعيين كل الرسائل غير المقروءة للعرض offer_id والتي ليست من المرسل الحالي كمقروءة
        Negotiation.objects.filter(
            offer_id=offer_id,
            is_read=False
        ).exclude(sender=user).update(is_read=True)
        return Response({"detail": "Messages marked as read."})

from .models import InvestmentOffer
from .serializer import NegotiationSerializer
class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id, investor_id):
        user = request.user
        message = request.data.get('message')

        if not message:
            return Response({'detail': 'Message content is required.'}, status=400)

        offer = InvestmentOffer.objects.filter(id=offer_id).first()
        if not offer:
            return Response({'detail': 'Offer not found.'}, status=404)

        if user.role == 'owner' and offer.project.owner.user != user:
            return Response({'detail': 'Unauthorized'}, status=403)

        if user.role == 'investor' and (user.id != int(investor_id) or offer.investor.id != user.id):
            return Response({'detail': 'Unauthorized'}, status=403)

        negotiation = Negotiation.objects.create(
            offer=offer,
            sender=user,
            investor=User.objects.get(id=investor_id),
            message=message,
            is_read=False
        )

        serializer = NegotiationSerializer(negotiation)
        return Response(serializer.data)


class ConversationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, offer_id, investor_id):
        user = request.user

        offer = InvestmentOffer.objects.filter(id=offer_id).first()
        if not offer:
            return Response({'detail': 'Offer not found'}, status=404)

        if not (user.role == 'owner' and offer.project.owner.user == user) and not (user.role == 'investor' and user.id == int(investor_id)):
            return Response({'detail': 'Unauthorized access'}, status=403)

        negotiations = Negotiation.objects.filter(offer=offer, investor__id=investor_id).order_by('timestamp')

        unread_messages = negotiations.filter(is_read=False).exclude(sender=user)
        unread_messages.update(is_read=True)

        serializer = NegotiationSerializer(negotiations, many=True)
        return Response(serializer.data)