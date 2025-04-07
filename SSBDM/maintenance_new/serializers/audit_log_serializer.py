from rest_framework import serializers
from ..models import AuditLog
from .maintenance_log_serializer import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model."""
    
    action_display = serializers.CharField(
        source='get_action_display',
        read_only=True
    )
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'action_display', 'model_name',
            'object_id', 'details', 'timestamp', 'created_at', 'created_by'
        ]
        read_only_fields = [
            'id', 'user', 'action', 'model_name', 'object_id',
            'details', 'timestamp', 'created_at', 'created_by'
        ]


class AuditLogDetailSerializer(AuditLogSerializer):
    """Serializer for AuditLog model with related data."""
    
    user = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta(AuditLogSerializer.Meta):
        fields = AuditLogSerializer.Meta.fields 