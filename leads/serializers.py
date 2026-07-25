from rest_framework import serializers
from .models import Lead, Note, Activity
from users.serializers import UserSerializer


class PublicLeadSerializer(serializers.ModelSerializer):
    """
    Serializer for public lead submission (no authentication required).
    """
    class Meta:
        model = Lead
        fields = ('full_name', 'email', 'phone', 'company', 'source')
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'source': {'default': 'website'},
        }
    
    def create(self, validated_data):
        # Set default values for public leads
        validated_data['status'] = 'new'
        validated_data['source'] = validated_data.get('source', 'website')
        return super().create(validated_data)


class LeadSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    status_display = serializers.CharField(read_only=True)
    source_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Lead
        fields = (
            'id', 'full_name', 'email', 'phone', 'company',
            'source', 'source_display', 'status', 'status_display',
            'assigned_to', 'assigned_to_detail', 'created_by', 'created_by_detail',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_by', 'created_at', 'updated_at')


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            'full_name', 'email', 'phone', 'company',
            'source', 'status', 'assigned_to'
        )


class LeadUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = (
            'full_name', 'email', 'phone', 'company',
            'source', 'status', 'assigned_to'
        )


class NoteSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Note
        fields = ('id', 'lead', 'user', 'user_detail', 'note', 'created_at', 'updated_at')
        read_only_fields = ('lead','user', 'created_at', 'updated_at')


class ActivitySerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = Activity
        fields = ('id', 'lead', 'user', 'user_detail', 'action', 'action_display', 'description', 'created_at')
        read_only_fields = ('user', 'created_at')