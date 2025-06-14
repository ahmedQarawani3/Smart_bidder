from rest_framework import serializers
from .models import Negotiation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name']

class NegotiationLastMessageSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Negotiation
        fields = ['id', 'message', 'timestamp', 'is_read', 'sender']




from rest_framework import serializers
from .models import Negotiation



class NegotiationSerializer(serializers.ModelSerializer):
    sender_full_name = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model = Negotiation
        fields = ['id', 'offer', 'sender', 'sender_full_name', 'investor', 'message', 'timestamp', 'is_read']

