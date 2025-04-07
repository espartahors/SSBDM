from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Equipment, Area, TechnicalSpecification
from ..serializers import (
    EquipmentSerializer,
    EquipmentDetailSerializer,
    TechnicalSpecificationSerializer,
    AreaSerializer,
    AreaTreeSerializer
)
from ..services import EquipmentService, AreaService, TechnicalSpecificationService
from ..permissions import EquipmentPermission, TechnicalSpecificationPermission


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for equipment.
    
    Provides CRUD operations and additional actions:
    - search
    - by_area
    - by_status
    - by_installation_date_range
    - recent
    """
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [EquipmentPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['area', 'status', 'installation_date']
    search_fields = ['name', 'code', 'description', 'model', 'manufacturer']
    ordering_fields = ['installation_date', 'name', 'code']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return EquipmentDetailSerializer
        return EquipmentSerializer
    
    def get_service(self):
        """Get equipment service instance."""
        return EquipmentService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new equipment using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        equipment = service.create(**data)
        serializer.instance = equipment
    
    def perform_update(self, serializer):
        """Update equipment using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        equipment = service.update(serializer.instance, **data)
        serializer.instance = equipment
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for equipment based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        equipment_list = service.search(query)
        page = self.paginate_queryset(equipment_list)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(equipment_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_area(self, request):
        """
        Get equipment by area.
        """
        area_id = request.query_params.get('area_id')
        if not area_id:
            return Response(
                {"error": "area_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        equipment_list = service.get_by_area(area_id)
        
        page = self.paginate_queryset(equipment_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(equipment_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get equipment by status.
        """
        status_value = request.query_params.get('status')
        if not status_value:
            return Response(
                {"error": "status parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        equipment_list = service.get_by_status(status_value)
        
        page = self.paginate_queryset(equipment_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(equipment_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_installation_date_range(self, request):
        """
        Get equipment by installation date range.
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {"error": "start_date and end_date parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        equipment_list = service.get_by_installation_date_range(start_date, end_date)
        
        page = self.paginate_queryset(equipment_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(equipment_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recently added equipment.
        """
        days = int(request.query_params.get('days', 30))
        service = self.get_service()
        equipment_list = service.get_recent(days=days)
        
        page = self.paginate_queryset(equipment_list)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(equipment_list, many=True)
        return Response(serializer.data)


class AreaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for equipment areas.
    
    Provides CRUD operations and additional actions:
    - search
    - equipment_count
    """
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [EquipmentPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    
    def get_service(self):
        """Get area service instance."""
        return AreaService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new area using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        area = service.create(**data)
        serializer.instance = area
    
    def perform_update(self, serializer):
        """Update area using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        area = service.update(serializer.instance, **data)
        serializer.instance = area
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for areas based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        areas = service.search(query)
        
        serializer = self.get_serializer(areas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def equipment_count(self, request, pk=None):
        """
        Get count of equipment in the area.
        """
        service = self.get_service()
        count = service.get_equipment_count(pk)
        
        return Response({
            'area_id': pk,
            'equipment_count': count
        })


class TechnicalSpecificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for technical specifications.
    
    Provides CRUD operations and additional actions:
    - search
    - by_equipment
    - by_spec_type
    """
    queryset = TechnicalSpecification.objects.all()
    serializer_class = TechnicalSpecificationSerializer
    permission_classes = [TechnicalSpecificationPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'spec_type']
    search_fields = ['name', 'value', 'spec_type']
    ordering_fields = ['name', 'spec_type']
    ordering = ['name']
    
    def get_service(self):
        """Get technical specification service instance."""
        return TechnicalSpecificationService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new technical specification using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        spec = service.create(**data)
        serializer.instance = spec
    
    def perform_update(self, serializer):
        """Update technical specification using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        spec = service.update(serializer.instance, **data)
        serializer.instance = spec
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for technical specifications based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        specs = service.search(query)
        
        serializer = self.get_serializer(specs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_equipment(self, request):
        """
        Get technical specifications for a specific equipment.
        """
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {"error": "equipment_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        specs = service.get_by_equipment(equipment_id)
        
        serializer = self.get_serializer(specs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_spec_type(self, request):
        """
        Get technical specifications by type.
        """
        spec_type = request.query_params.get('type')
        if not spec_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        specs = service.get_by_spec_type(spec_type)
        
        serializer = self.get_serializer(specs, many=True)
        return Response(serializer.data) 