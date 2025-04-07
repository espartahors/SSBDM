from rest_framework import serializers
from ..models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'description', 'parent']
        read_only_fields = ['id']


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer for Category model with tree structure."""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'description', 'children']
        read_only_fields = ['id']
    
    def get_children(self, obj):
        """Get serialized children of the category."""
        return CategoryTreeSerializer(obj.get_children(), many=True).data 