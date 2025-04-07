from rest_framework import serializers
from ..models import MaintenancePlan
from equipment_new.models import Equipment
from equipment_new.serializers import EquipmentSerializer
from .maintenance_log_serializer import UserSerializer


class MaintenancePlanSerializer(serializers.ModelSerializer):
    """Serializer for MaintenancePlan model."""
    
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all()
    )
    
    maintenance_type_display = serializers.CharField(
        source='get_maintenance_type_display',
        read_only=True
    )
    frequency_display = serializers.CharField(
        source='get_frequency_display',
        read_only=True
    )
    
    class Meta:
        model = MaintenancePlan
        fields = [
            'id', 'code', 'name', 'equipment', 'maintenance_type', 'maintenance_type_display',
            'title', 'description', 'frequency', 'frequency_display', 'frequency_value',
            'start_date', 'end_date', 'estimated_duration', 'is_active',
            'last_executed', 'next_due', 'notes', 'created_at', 'created_by',
            'updated_at', 'updated_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'created_by', 'updated_at', 'updated_by'
        ]


class MaintenancePlanDetailSerializer(MaintenancePlanSerializer):
    """Serializer for MaintenancePlan model with related data."""
    
    equipment = EquipmentSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    recent_logs = serializers.SerializerMethodField()
    
    class Meta(MaintenancePlanSerializer.Meta):
        fields = MaintenancePlanSerializer.Meta.fields + ['recent_logs']
    
    def get_recent_logs(self, obj):
        """Get recent maintenance logs for the plan."""
        # Importing here to avoid circular imports
        from ..models import MaintenanceLog
        
        # Get logs with the same title pattern and equipment
        logs = MaintenanceLog.objects.filter(
            equipment=obj.equipment,
            title__startswith=f"Plan: {obj.title}"
        ).order_by('-date')[:5]
        
        # Return basic log information
        return [
            {
                'id': log.id,
                'date': log.date,
                'result': log.maintenance_result,
                'result_display': log.get_maintenance_result_display() if log.maintenance_result else None,
                'duration': log.duration
            }
            for log in logs
        ] 