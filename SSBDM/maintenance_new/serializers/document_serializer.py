from rest_framework import serializers
from ..models import EquipmentDocument
from equipment_new.models import Equipment
from equipment_new.serializers import EquipmentSerializer
from .maintenance_log_serializer import UserSerializer


class EquipmentDocumentSerializer(serializers.ModelSerializer):
    """Serializer for EquipmentDocument model."""
    
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all()
    )
    
    document_type_display = serializers.CharField(
        source='get_document_type_display',
        read_only=True
    )
    filename = serializers.CharField(read_only=True)
    
    class Meta:
        model = EquipmentDocument
        fields = [
            'id', 'equipment', 'title', 'document_type', 'document_type_display',
            'file', 'upload_date', 'description', 'filename',
            'created_at', 'created_by', 'updated_at', 'updated_by'
        ]
        read_only_fields = [
            'id', 'upload_date', 'created_at', 'created_by', 'updated_at', 'updated_by'
        ]


class EquipmentDocumentDetailSerializer(EquipmentDocumentSerializer):
    """Serializer for EquipmentDocument model with related data."""
    
    equipment = EquipmentSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)
    
    class Meta(EquipmentDocumentSerializer.Meta):
        fields = EquipmentDocumentSerializer.Meta.fields 