from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import MaintenanceLog
from equipment_new.models import Equipment
from equipment_new.serializers import EquipmentSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class MaintenanceLogSerializer(serializers.ModelSerializer):
    """Serializer for MaintenanceLog model."""
    
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all()
    )
    technicians = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True
    )
    
    maintenance_type_display = serializers.CharField(
        source='get_maintenance_type_display',
        read_only=True
    )
    maintenance_result_display = serializers.CharField(
        source='get_maintenance_result_display',
        read_only=True
    )
    
    class Meta:
        model = MaintenanceLog
        fields = [
            'id', 'equipment', 'maintenance_type', 'maintenance_type_display',
            'title', 'description', 'date', 'duration', 'technicians',
            'observations', 'maintenance_result', 'maintenance_result_display',
            'result_description', 'notes', 'created_at', 'created_by',
            'updated_at', 'updated_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'created_by', 'updated_at', 'updated_by'
        ]


class MaintenanceLogDetailSerializer(MaintenanceLogSerializer):
    """Serializer for MaintenanceLog model with related data."""
    
    equipment = EquipmentSerializer(read_only=True)
    technicians = UserSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    tasks = serializers.SerializerMethodField()
    
    class Meta(MaintenanceLogSerializer.Meta):
        fields = MaintenanceLogSerializer.Meta.fields + ['tasks']
    
    def get_tasks(self, obj):
        """Get maintenance tasks for the log."""
        from ..serializers import MaintenanceTaskSerializer
        tasks = obj.tasks.all().order_by('-due_date')
        return MaintenanceTaskSerializer(tasks, many=True).data 