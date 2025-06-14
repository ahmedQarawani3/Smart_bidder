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



from rest_framework import serializers
from .models import Negotiation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'full_name']

class NegotiationSerializer(serializers.ModelSerializer):
    sender = UserSimpleSerializer(read_only=True)
    from_me = serializers.SerializerMethodField()

    class Meta:
        model = Negotiation
        fields = ['id', 'offer', 'sender', 'message', 'timestamp', 'is_read', 'from_me']

    def get_from_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False


