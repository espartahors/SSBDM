from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from ..models import MaintenanceLog
from ..serializers import MaintenanceLogSerializer, MaintenanceLogDetailSerializer
from ..services import MaintenanceLogService
from ..permissions import MaintenancePermission


class MaintenanceLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for maintenance logs.
    
    Provides CRUD operations and additional actions:
    - search
    - by_equipment
    - by_type
    - by_date_range
    - by_result
    - recent
    - statistics
    """
    queryset = MaintenanceLog.objects.all()
    serializer_class = MaintenanceLogSerializer
    permission_classes = [MaintenancePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'maintenance_type', 'maintenance_result', 'date']
    search_fields = ['title', 'description', 'observations', 'result_description']
    ordering_fields = ['date', 'created_at', 'updated_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return MaintenanceLogDetailSerializer
        return MaintenanceLogSerializer
    
    def get_service(self):
        """Get maintenance log service instance."""
        return MaintenanceLogService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new maintenance log using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        log = service.create(**data)
        serializer.instance = log
    
    def perform_update(self, serializer):
        """Update maintenance log using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        log = service.update(serializer.instance, **data)
        serializer.instance = log
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for maintenance logs based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.search(query)
        page = self.paginate_queryset(logs)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_equipment(self, request):
        """
        Get maintenance logs for a specific equipment.
        """
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {"error": "equipment_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.get_by_equipment(equipment_id)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get maintenance logs by type.
        """
        maintenance_type = request.query_params.get('type')
        if not maintenance_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.get_by_type(maintenance_type)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """
        Get maintenance logs within a date range.
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {"error": "start_date and end_date parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.get_by_date_range(start_date, end_date)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_result(self, request):
        """
        Get maintenance logs by result.
        """
        result = request.query_params.get('result')
        if not result:
            return Response(
                {"error": "result parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.get_by_result(result)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent maintenance logs.
        """
        days = int(request.query_params.get('days', 30))
        service = self.get_service()
        logs = service.get_recent_logs(days=days)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get maintenance log statistics.
        """
        days = int(request.query_params.get('days', 30))
        service = self.get_service()
        stats = service.get_statistics(days=days)
        return Response(stats) 