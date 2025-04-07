from rest_framework import serializers
from ..models import SparePart, Category
from .category_serializer import CategorySerializer


class SparePartSerializer(serializers.ModelSerializer):
    """Serializer for SparePart model."""
    
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    
    stock_status = serializers.CharField(source='get_stock_status', read_only=True)
    stock_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = SparePart
        fields = [
            'id', 'code', 'name', 'description', 'current_stock', 'minimum_stock',
            'unit', 'price', 'currency', 'location', 'manufacturer', 'supplier',
            'supplier_reference', 'lead_time', 'notes', 'image', 'category',
            'stock_status', 'stock_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SparePartDetailSerializer(SparePartSerializer):
    """Serializer for SparePart model with related data."""
    
    category = CategorySerializer(read_only=True)
    transactions = serializers.SerializerMethodField()
    
    class Meta(SparePartSerializer.Meta):
        fields = SparePartSerializer.Meta.fields + ['transactions']
    
    def get_transactions(self, obj):
        """Get recent transactions for the spare part."""
        from ..models import SparePartTransaction
        from .transaction_serializer import SparePartTransactionSerializer
        transactions = obj.transactions.all().order_by('-date')[:10]
        return SparePartTransactionSerializer(transactions, many=True).data 