from rest_framework import serializers
from ..models import SparePartTransaction, SparePart
from equipment_new.models import Equipment
from equipment_new.serializers import EquipmentSerializer
from .spare_part_serializer import SparePartSerializer


class SparePartTransactionSerializer(serializers.ModelSerializer):
    """Serializer for SparePartTransaction model."""
    
    spare_part = serializers.PrimaryKeyRelatedField(queryset=SparePart.objects.all())
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        required=False,
        allow_null=True
    )
    
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    
    class Meta:
        model = SparePartTransaction
        fields = [
            'id', 'spare_part', 'transaction_type', 'transaction_type_display',
            'quantity', 'unit_price', 'equipment', 'date', 'reference',
            'created_at', 'created_by'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']


class SparePartTransactionDetailSerializer(SparePartTransactionSerializer):
    """Serializer for SparePartTransaction model with related data."""
    
    spare_part = SparePartSerializer(read_only=True)
    equipment = EquipmentSerializer(read_only=True)
    
    class Meta(SparePartTransactionSerializer.Meta):
        fields = SparePartTransactionSerializer.Meta.fields 