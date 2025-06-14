from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max, Q
from .models import Negotiation
from django.contrib.auth import get_user_model
from projectOwner.models import Project
User = get_user_model()

from django.db.models import Q, Max, Count, Case, When, BooleanField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from .models import Negotiation, Project  # تأكد من استيراد النماذج الضرورية

class ConversationsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'investor':
            negotiations = Negotiation.objects.filter(sender=user) | Negotiation.objects.filter(offer__investor=user)
            negotiations = negotiations.distinct()
        elif user.role == 'owner':
            negotiations = Negotiation.objects.filter(offer__project__owner__user=user)
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

        last_msgs = negotiations.values('offer_id').annotate(last_timestamp=Max('timestamp'))

        conversations = []
        for item in last_msgs:
            offer_id = item['offer_id']
            last_time = item['last_timestamp']

            last_msg = Negotiation.objects.filter(offer_id=offer_id, timestamp=last_time).first()
            offer = last_msg.offer
            project = offer.project  # ← هنا أخذنا المشروع

            if user.role == 'investor':
                other_user = offer.project.owner.user
            else:
                other_user = offer.investor.user

            unread_exists = Negotiation.objects.filter(
                offer_id=offer_id,
                is_read=False
            ).exclude(sender=user).exists()

            conversations.append({
                'offer_id': offer_id,
                'other_user_id': other_user.id,
                'other_user_full_name': other_user.full_name,
                'last_message': last_msg.message,
                'last_message_time': last_msg.timestamp,
                'is_read': not unread_exists,
                'project_title': project.title  # ← هنا أضفنا اسم المشروع
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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import InvestmentOffer, Negotiation
from .serializer import NegotiationSerializer

class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        user = request.user
        message = request.data.get('message')

        if not message:
            return Response({'detail': 'Message content is required.'}, status=400)

        offer = get_object_or_404(InvestmentOffer, id=offer_id)

        # تحقق من الصلاحية حسب الدور
        if user.role == 'owner' and offer.project.owner.user != user:
            return Response({'detail': 'Unauthorized'}, status=403)

        if user.role == 'investor' and offer.investor.user != user:
            return Response({'detail': 'Unauthorized'}, status=403)

        negotiation = Negotiation.objects.create(
            offer=offer,
            sender=user,
            message=message,
            is_read=False
        )

        serializer = NegotiationSerializer(negotiation, context={'request': request})
        return Response(serializer.data, status=201)



from django.db.models import Q



class ConversationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, offer_id):
        user = request.user
        offer = InvestmentOffer.objects.filter(id=offer_id).first()

        if not offer:
            return Response({'detail': 'Offer not found'}, status=404)
        if not (
            (user.role == 'owner' and offer.project.owner.user == user) or
            (user.role == 'investor' and offer.investor.user == user)
        ):
            return Response({'detail': 'Unauthorized access'}, status=403)
        other_user = offer.project.owner.user if user.role == 'investor' else offer.investor.user
        negotiations = Negotiation.objects.filter(
            offer=offer
        ).filter(
            Q(sender=user) | Q(sender=other_user)
        ).order_by('timestamp')
        unread_messages = negotiations.filter(is_read=False).exclude(sender=user)
        unread_messages.update(is_read=True)

        serializer = NegotiationSerializer(negotiations, many=True, context={'request': request})
        return Response(serializer.data)


