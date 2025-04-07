from rest_framework import serializers
from ..models import Equipment, TechnicalSpecification, Area


class AreaSerializer(serializers.ModelSerializer):
    """Serializer for Area model."""
    
    class Meta:
        model = Area
        fields = ['id', 'code', 'name', 'description', 'parent']
        read_only_fields = ['id']


class AreaTreeSerializer(serializers.ModelSerializer):
    """Serializer for Area model with tree structure."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Area
        fields = ['id', 'code', 'name', 'description', 'children']
        read_only_fields = ['id']
    
    def get_children(self, obj):
        """Get serialized children of the area."""
        return AreaTreeSerializer(obj.get_children(), many=True).data


class TechnicalSpecificationSerializer(serializers.ModelSerializer):
    """Serializer for TechnicalSpecification model."""
    
    class Meta:
        model = TechnicalSpecification
        fields = ['id', 'specification', 'value', 'unit']
        read_only_fields = ['id']


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model."""
    
    area = AreaSerializer(read_only=True)
    area_id = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all(),
        source='area',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        required=False,
        allow_null=True
    )
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_type_display = serializers.CharField(source='get_equipment_type_display', read_only=True)
    maintenance_status = serializers.CharField(source='get_maintenance_status', read_only=True)
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'code', 'name', 'description', 'equipment_type', 'equipment_type_display',
            'area', 'area_id', 'parent', 'manufacturer', 'model', 'serial_number',
            'installation_date', 'status', 'status_display', 'notes',
            'purchase_date', 'purchase_cost', 'warranty_expiration', 'expected_lifetime',
            'is_critical', 'last_maintenance_date', 'next_maintenance_date',
            'maintenance_interval', 'maintenance_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EquipmentDetailSerializer(EquipmentSerializer):
    """Serializer for Equipment model with related data."""
    
    technical_specifications = TechnicalSpecificationSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta(EquipmentSerializer.Meta):
        fields = EquipmentSerializer.Meta.fields + ['technical_specifications', 'children']
    
    def get_children(self, obj):
        """Get serialized children of the equipment."""
        return EquipmentSerializer(obj.get_all_children(), many=True).data 