# serializers.py
from rest_framework import serializers
from .models import Negotiation,InvestmentOffer

from rest_framework import serializers
from .models import Negotiation

class NegotiationSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Negotiation
        fields = ['id', 'message', 'timestamp', 'is_read', 'sender_name', 'is_owner']
        read_only_fields = ['sender', 'offer', 'timestamp', 'is_read']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username

    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request and obj.sender == request.user
  

class NegotiationConversationSerializer(serializers.ModelSerializer):
    project_title = serializers.SerializerMethodField()
    other_user_name = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = InvestmentOffer
        fields = [
            'id',
            'project_title',
            'other_user_name',
            'last_message',
            'last_message_time',
            'unread_count',
        ]

    def get_project_title(self, obj):
        return obj.project.title

    def get_other_user_name(self, obj):
        user = self.context['request'].user
        if user == obj.project.owner.user:
            return obj.investor.user.get_full_name()
        return obj.project.owner.user.get_full_name()

    def get_last_message(self, obj):
        last = obj.negotiations.order_by('-timestamp').first()
        return last.message if last else ""

    def get_last_message_time(self, obj):
        last = obj.negotiations.order_by('-timestamp').first()
        return last.timestamp.strftime('%m/%d/%Y') if last else None

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return obj.negotiations.filter(is_read=False).exclude(sender=user).count()