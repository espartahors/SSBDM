from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import MaintenanceTask, MaintenanceLog
from .maintenance_log_serializer import UserSerializer


class MaintenanceTaskSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceTask model."""
    
    maintenance_log = serializers.PrimaryKeyRelatedField(
        queryset=MaintenanceLog.objects.all()
    )
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = MaintenanceTask
        fields = [
            'id', 'maintenance_log', 'description', 'status', 'status_display',
            'assigned_to', 'due_date', 'completed_date', 'notes',
            'created_at', 'created_by', 'updated_at', 'updated_by',
            'is_overdue'
        ]
        read_only_fields = [
            'id', 'created_at', 'created_by', 'updated_at', 'updated_by'
        ]


class MaintenanceTaskDetailSerializer(MaintenanceTaskSerializer):
    """Serializer for MaintenanceTask model with related data."""
    
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    maintenance_log_details = serializers.SerializerMethodField()
    
    class Meta(MaintenanceTaskSerializer.Meta):
        fields = MaintenanceTaskSerializer.Meta.fields + ['maintenance_log_details']
    
    def get_maintenance_log_details(self, obj):
        """Get basic details of the maintenance log."""
        return {
            'id': obj.maintenance_log.id,
            'title': obj.maintenance_log.title,
            'equipment_code': obj.maintenance_log.equipment.code,
            'equipment_name': obj.maintenance_log.equipment.name,
            'date': obj.maintenance_log.date
        } 