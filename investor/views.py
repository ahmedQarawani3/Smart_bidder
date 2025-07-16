from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max, Q
from .models import Negotiation
from django.contrib.auth import get_user_model
from projectOwner.models import Project
User = get_user_model()
from rest_framework import generics, permissions, status
from projectOwner.serializer import ProjectDetailsSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Negotiation
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, Max, Count, Case, When, BooleanField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Max
from .models import Negotiation, Project  # تأكد من استيراد النماذج الضرورية
from .models import InvestmentOffer
from .serializer import NegotiationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import InvestmentOffer, Negotiation
from .serializer import NegotiationSerializer
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework import generics, permissions
from django.db.models import Q
from .serializer import ProjectFundingSerializer
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from projectOwner.serializer import ProjectSerializer
from .models import Project, InvestmentOffer,Investor
from .serializer import InvestmentOfferCreateSerializer

# عرض جميع المحادثات
class ConversationsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'investor':
            try:
                investor = user.investor
            except Investor.DoesNotExist:
                return Response({'detail': 'Investor profile not found.'}, status=404)

            offers = InvestmentOffer.objects.filter(investor=investor)
        
        elif user.role == 'owner':
            offers = InvestmentOffer.objects.filter(project__owner__user=user)
        
        else:
            return Response({'detail': 'Unauthorized'}, status=403)

        negotiations = Negotiation.objects.filter(offer__in=offers)

        last_msgs = negotiations.values('offer_id').annotate(last_timestamp=Max('timestamp'))

        conversations = []
        for item in last_msgs:
            offer_id = item['offer_id']
            last_time = item['last_timestamp']

            last_msg = Negotiation.objects.filter(
                offer_id=offer_id,
                timestamp=last_time
            ).first()

            offer = last_msg.offer
            project = offer.project

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
                'project_title': project.title,
            })

        conversations.sort(key=lambda x: x['last_message_time'], reverse=True)

        return Response(conversations)

#تعيين الرسائل كمقروءة
class MarkMessagesReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        user = request.user

        Negotiation.objects.filter(
            offer_id=offer_id,
            is_read=False
        ).exclude(sender=user).update(is_read=True)

        return Response({"detail": "Messages marked as read."})
# إرسال رسالة

class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, offer_id):
        user = request.user
        message = request.data.get('message')

        if not message:
            return Response({'detail': 'Message content is required.'}, status=400)

        offer = get_object_or_404(InvestmentOffer, id=offer_id)

        if user.role == 'owner':
            if offer.project.owner.user != user:
                return Response({'detail': 'Unauthorized'}, status=403)

        elif user.role == 'investor':
            try:
                investor = user.investor
            except Investor.DoesNotExist:
                return Response({'detail': 'Investor profile not found.'}, status=404)

            if offer.investor != investor:
                return Response({'detail': 'Unauthorized'}, status=403)

            # ✅ التحقق إن صاحب المشروع بدأ المحادثة
            has_owner_message = Negotiation.objects.filter(
                offer=offer,
                sender=offer.project.owner.user  # تأكد أن العلاقة صحيحة
            ).exists()

            if not has_owner_message:
                return Response({
                    'detail': 'You cannot start the negotiation. Please wait for the project owner to initiate.'
                }, status=403)

        else:
            return Response({'detail': 'Unauthorized role'}, status=403)

        # ✅ إنشاء الرسالة الجديدة
        negotiation = Negotiation.objects.create(
            offer=offer,
            sender=user,
            message=message,
            is_read=False
        )

        serializer = NegotiationSerializer(negotiation, context={'request': request})
        return Response(serializer.data, status=201)



#عرض تفاصيل محادثة معينة
class ConversationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, offer_id):
        user = request.user
        offer = InvestmentOffer.objects.filter(id=offer_id).first()

        if not offer:
            return Response({'detail': 'Offer not found'}, status=404)

        if not (
            (user.role == 'owner' and offer.project.owner.user == user) or
            (user.role == 'investor' and hasattr(user, 'investor') and offer.investor == user.investor)
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

#عرض تفاصبل المشروع للمسثمر 
class ProjectDetailView(RetrieveAPIView):
    """
    عرض تفاصيل مشروع معين عند الضغط عليه من قبل المستثمر
    """
    queryset = Project.objects.all()
    serializer_class = ProjectDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        # التحقق من أن المستخدم مستثمر فقط
        if not hasattr(user, 'role') or user.role != 'investor':
            raise PermissionDenied("فقط المستثمر يمكنه رؤية تفاصيل المشروع.")

        return super().get_object()

#عرض المشاريع للمستثمر
class ProjectFundingOnlyListView(generics.ListAPIView):
    """
    عرض المشاريع مع التمويل المطلوب فقط، للمستثمرين فقط
    """
    serializer_class = ProjectFundingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if not hasattr(user, 'role') or user.role != 'investor':
            raise PermissionDenied("فقط المستثمر يمكنه رؤية هذه المشاريع.")

        return Project.objects.filter(
            Q(status='active') | Q(status='under_negotiation')
        )

from projectOwner.utils import auto_close_project_if_expired

class CreateInvestmentOfferView(generics.CreateAPIView):
    serializer_class = InvestmentOfferCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, 'role') or user.role != 'investor':
            raise PermissionDenied("Only investors can send offers.")

        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)

        # 🔴 التحقق إذا المستثمر قدم عرض سابق لهذا المشروع
        existing_offer = InvestmentOffer.objects.filter(investor=user.investor, project=project).first()
        if existing_offer:
            raise PermissionDenied("You have already submitted an offer for this project.")

        # إذا ما في عرض سابق، بيتم إنشاء عرض جديد
        offer = serializer.save(investor=user.investor, project=project)

        # التحقق من إغلاق المشروع تلقائيًا بعد العرض
        auto_close_project_if_expired(project)


class FilteredProjectList(APIView):
    def get(self, request):
        projects = Project.objects.filter(status='active')

        category = request.GET.get('category')
        readiness_level = request.GET.get('readiness_level')
        min_funding = request.GET.get('min_funding')
        max_funding = request.GET.get('max_funding')
        max_roi_period = request.GET.get('max_roi_period')
        sort_by = request.GET.get('sort_by')

        # فلتر التصنيف
        if category and category != 'all':
            projects = projects.filter(category=category)

        # فلتر الجاهزية
        if readiness_level and readiness_level != 'all':
            projects = projects.filter(readiness_level=readiness_level)

        # فلتر التمويل
        if min_funding:
            projects = projects.filter(feasibility_study__funding_required__gte=min_funding)

        if max_funding:
            projects = projects.filter(feasibility_study__funding_required__lte=max_funding)

        # فلتر فترة استرداد رأس المال
        if max_roi_period:
            projects = projects.filter(feasibility_study__roi_period_months__lte=max_roi_period)

        # ترتيب النتائج
        if sort_by == 'newest':
            projects = projects.order_by('-created_at')
        elif sort_by == 'oldest':
            projects = projects.order_by('created_at')

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .serializer import OfferStatisticsSerializer
#عرض من عند صفحه العروض من فوق تبع كم عرض مقدك وهدول الشغلات
class InvestorOfferStatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not hasattr(user, 'investor'):
            return Response({'detail': 'User is not an investor.'}, status=403)

        offers = InvestmentOffer.objects.filter(investor=user.investor)

        total_offers = offers.count()
        pending_offers = offers.filter(status='pending').count()
        accepted_offers = offers.filter(status='accepted').count()
        rejected_offers = offers.filter(status='rejected').count()
        total_invested_amount = offers.filter(status='accepted').aggregate(
            total=Sum('amount'))['total'] or 0

        data = {
            "total_offers": total_offers,
            "pending_offers": pending_offers,
            "accepted_offers": accepted_offers,
            "rejected_offers": rejected_offers,
            "total_invested_amount": total_invested_amount,
        }

        serializer = OfferStatisticsSerializer(data)
        return Response(serializer.data)

from .serializer import InvestmentOfferSerializer

class MyOffersListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # تحقق من أن المستخدم هو مستثمر
        if user.role != 'investor':
            return Response({'detail': 'Unauthorized'}, status=403)

        try:
            investor = user.investor
        except:
            return Response({'detail': 'Investor profile not found.'}, status=404)

        # جلب كل العروض المقدمة من هذا المستثمر
        offers = InvestmentOffer.objects.filter(investor=investor).select_related('project')

        serializer = InvestmentOfferSerializer(offers, many=True)
        return Response(serializer.data)


from rest_framework import generics, permissions
from .serializer import InvestorUpdateSerializer

class UpdateInvestorProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = InvestorUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.investor


from accounts.models import Notification
class RejectOfferView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, offer_id):
        try:
            offer = InvestmentOffer.objects.select_related('project__owner__user').get(id=offer_id)
        except InvestmentOffer.DoesNotExist:
            return Response({"detail": "Offer not found."}, status=status.HTTP_404_NOT_FOUND)

        if offer.project.owner.user != request.user:
            return Response({"detail": "You are not authorized to reject this offer."}, status=status.HTTP_403_FORBIDDEN)

        offer.status = 'rejected'
        offer.rejection_reason = 'owner_rejected'  # إذا عندك الحقل في الموديل
        offer.save(update_fields=['status', 'rejection_reason'])

        # إشعار المستثمر بأن العرض رفضه صاحب المشروع
        message = f"Your investment offer for the project '{offer.project.title}' has been rejected by the project owner."
        Notification.objects.create(user=offer.investor.user, message=message)

        return Response({"detail": "Offer rejected successfully."}, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from investor.models import Investor
from projectOwner.models import ProjectOwner
from .serializer import InvestorSerializer, ProjectOwnerSerializer 
class TopInvestorsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        investors = Investor.objects.filter(rating_score__gt=0).order_by('-rating_score')[:5]
        serializer = InvestorSerializer(investors, many=True)
        return Response(serializer.data)