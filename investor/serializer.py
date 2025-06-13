# serializers.py
from rest_framework import serializers
from .models import Negotiation,InvestmentOffer

class NegotiationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    is_sent_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Negotiation
        fields = '__all__'
        read_only_fields = ['sender', 'offer', 'timestamp', 'is_read']

    def get_sender_name(self, obj):
        request_user = self.context['request'].user
        if obj.sender == request_user:
            # لا ترجع اسم المستخدم الحالي
            return None
        return obj.sender.get_full_name() or obj.sender.username


    def get_receiver_name(self, obj):
        request_user = self.context['request'].user
        if obj.offer.investor.user == request_user:
            return obj.offer.project.owner.user.get_full_name()
        return obj.offer.investor.user.get_full_name()

    def get_is_sent_by_user(self, obj):
        request_user = self.context['request'].user
        return obj.sender == request_user
from django.db.models import Q

  

class NegotiationConversationSerializer(serializers.ModelSerializer):
    project_title = serializers.SerializerMethodField()
    other_user_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    messages = serializers.SerializerMethodField()

    class Meta:
        model = InvestmentOffer
        fields = [
            'id',
            'project_title',
            'other_user_name',
            'last_message',
            'last_message_time',
            'unread_count',
            'messages',
        ]

    def get_project_title(self, obj):
        return obj.project.title

    def get_other_user_name(self, obj):
        user = self.context['request'].user
        if user == obj.project.owner.user:
            return obj.investor.user.get_full_name()
        elif user == obj.investor.user:
            return obj.project.owner.user.get_full_name()
        return None

    def get_last_message(self, obj):
        user = self.context['request'].user
        last = obj.negotiations.filter(
            Q(sender=user) | Q(offer__investor__user=user) | Q(offer__project__owner__user=user)
        ).order_by('-timestamp').first()
        return last.message if last else ""

    def get_last_message_time(self, obj):
        user = self.context['request'].user
        last = obj.negotiations.filter(
            Q(sender=user) | Q(offer__investor__user=user) | Q(offer__project__owner__user=user)
        ).order_by('-timestamp').first()
        return last.timestamp.strftime('%m/%d/%Y') if last else None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.negotiations.filter(
            is_read=False
        ).exclude(sender=user).filter(
            Q(sender=user) | Q(offer__investor__user=user) | Q(offer__project__owner__user=user)
        ).count()

    def get_messages(self, obj):
        user = self.context['request'].user
        messages_qs = obj.negotiations.filter(
            Q(sender=user) | Q(offer__investor__user=user) | Q(offer__project__owner__user=user)
        ).order_by('timestamp')
        return NegotiationMessageSerializer(messages_qs, many=True).data




class NegotiationMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name')
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Negotiation
        fields = ['id', 'message', 'timestamp', 'is_read', 'sender_name', 'is_owner']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and obj.sender == request.user