from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Category
from ..serializers import CategorySerializer, CategoryTreeSerializer
from ..services import CategoryService
from ..permissions import CategoryPermission


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for spare part categories.
    
    Provides CRUD operations and additional actions:
    - tree
    - statistics
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['name', 'code', 'created_at', 'updated_at']
    ordering = ['code']
    
    def get_service(self):
        """Get category service instance."""
        return CategoryService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new category using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        category = service.create(**data)
        serializer.instance = category
    
    def perform_update(self, serializer):
        """Update category using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        category = service.update(serializer.instance, **data)
        serializer.instance = category
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Get category tree structure.
        """
        # Get only root categories (those without parents)
        categories = Category.objects.filter(parent=None)
        serializer = CategoryTreeSerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get category statistics.
        """
        service = self.get_service()
        stats = service.get_category_statistics()
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def spare_parts(self, request, pk=None):
        """
        Get spare parts in this category.
        """
        from ..services import SparePartService
        
        category = self.get_object()
        spare_part_service = SparePartService(user=request.user)
        spare_parts = spare_part_service.get_by_category(category.id)
        
        from ..serializers import SparePartSerializer
        page = self.paginate_queryset(spare_parts)
        if page is not None:
            serializer = SparePartSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SparePartSerializer(spare_parts, many=True)
        return Response(serializer.data) 