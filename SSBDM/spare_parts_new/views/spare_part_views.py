from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import SparePart
from ..serializers import SparePartSerializer, SparePartDetailSerializer
from ..services import SparePartService
from ..permissions import SparePartPermission


class SparePartViewSet(viewsets.ModelViewSet):
    """
    API endpoint for spare parts.
    
    Provides CRUD operations and additional actions:
    - search
    - by_category
    - low_stock
    - compatible_with
    """
    queryset = SparePart.objects.all()
    serializer_class = SparePartSerializer
    permission_classes = [SparePartPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'location']
    search_fields = ['name', 'part_number', 'description', 'manufacturer']
    ordering_fields = ['name', 'part_number', 'stock_level', 'last_ordered']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return SparePartDetailSerializer
        return SparePartSerializer
    
    def get_service(self):
        """Get spare part service instance."""
        return SparePartService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new spare part using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        part = service.create(**data)
        serializer.instance = part
    
    def perform_update(self, serializer):
        """Update spare part using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        part = service.update(serializer.instance, **data)
        serializer.instance = part
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for spare parts based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        parts = service.search(query)
        page = self.paginate_queryset(parts)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get spare parts by category.
        """
        category_id = request.query_params.get('category_id')
        if not category_id:
            return Response(
                {"error": "category_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        parts = service.get_by_category(category_id)
        
        page = self.paginate_queryset(parts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Get spare parts with low stock levels.
        """
        threshold = int(request.query_params.get('threshold', 5))
        
        service = self.get_service()
        parts = service.get_low_stock(threshold=threshold)
        
        page = self.paginate_queryset(parts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def compatible_with(self, request):
        """
        Get spare parts compatible with specific equipment.
        """
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {"error": "equipment_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        parts = service.get_compatible_with_equipment(equipment_id)
        
        page = self.paginate_queryset(parts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(parts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """
        Get transactions for this spare part.
        """
        from ..services import TransactionService
        
        spare_part = self.get_object()
        transaction_service = TransactionService(user=request.user)
        transactions = transaction_service.get_by_spare_part(spare_part.id)
        
        from ..serializers import SparePartTransactionSerializer
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = SparePartTransactionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SparePartTransactionSerializer(transactions, many=True)
        return Response(serializer.data) 