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

        negotiations = Negotiation.objects.filter(
            Q(sender=user) | Q(offer__project__owner__user=user) | Q(offer__investor__user=user)
        ).select_related('sender', 'offer', 'offer__project__owner__user', 'offer__investor__user')

        last_msgs = negotiations.values('offer').annotate(last_timestamp=Max('timestamp'))

        conversations = []
        for item in last_msgs:
            offer_id = item['offer']
            last_time = item['last_timestamp']
            last_msg = negotiations.filter(offer_id=offer_id, timestamp=last_time).first()

            offer = last_msg.offer

            # الطرف الآخر في المحادثة
            if user == last_msg.sender:
                if user.role == 'investor':
                    other_user = offer.project.owner.user
                else:
                    other_user = offer.investor.user
            else:
                other_user = last_msg.sender

            # **نحسب هل هناك رسائل غير مقروءة للمستخدم داخل هذا العرض**
            unread_exists = negotiations.filter(
                offer=offer_id,
                is_read=False
            ).exclude(sender=user).exists()

            conversations.append({
                'offer_id': offer_id,
                'other_user_id': other_user.id,
                'other_user_full_name': other_user.full_name,
                'last_message': last_msg.message,
                'last_message_time': last_msg.timestamp,
                'is_read': not unread_exists,  # إذا لا يوجد غير مقروءة -> True
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
