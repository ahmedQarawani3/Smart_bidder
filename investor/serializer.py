# serializers.py

from rest_framework import serializers
from .models import Negotiation

class NegotiationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Negotiation
        fields = ['id', 'offer', 'sender', 'sender_name', 'message', 'timestamp']
        read_only_fields = ['id', 'offer', 'sender', 'timestamp']
