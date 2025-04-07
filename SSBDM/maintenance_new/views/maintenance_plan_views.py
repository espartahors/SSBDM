from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from ..models import MaintenancePlan
from ..serializers import MaintenancePlanSerializer, MaintenancePlanDetailSerializer
from ..services import MaintenancePlanService
from ..permissions import MaintenancePermission


class MaintenancePlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for maintenance plans.
    
    Provides CRUD operations and additional actions:
    - search
    - by_equipment
    - by_status
    - by_frequency
    - active
    - generate_tasks
    """
    queryset = MaintenancePlan.objects.all()
    serializer_class = MaintenancePlanSerializer
    permission_classes = [MaintenancePermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'status', 'frequency', 'last_executed']
    search_fields = ['title', 'description', 'procedures']
    ordering_fields = ['last_executed', 'next_due', 'created_at', 'updated_at']
    ordering = ['next_due']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return MaintenancePlanDetailSerializer
        return MaintenancePlanSerializer
    
    def get_service(self):
        """Get maintenance plan service instance."""
        return MaintenancePlanService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new maintenance plan using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        plan = service.create(**data)
        serializer.instance = plan
    
    def perform_update(self, serializer):
        """Update maintenance plan using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        plan = service.update(serializer.instance, **data)
        serializer.instance = plan
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for maintenance plans based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        plans = service.search(query)
        page = self.paginate_queryset(plans)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_equipment(self, request):
        """
        Get maintenance plans for a specific equipment.
        """
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {"error": "equipment_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        plans = service.get_by_equipment(equipment_id)
        
        page = self.paginate_queryset(plans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get maintenance plans by status.
        """
        status_value = request.query_params.get('status')
        if not status_value:
            return Response(
                {"error": "status parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        plans = service.get_by_status(status_value)
        
        page = self.paginate_queryset(plans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_frequency(self, request):
        """
        Get maintenance plans by frequency.
        """
        frequency = request.query_params.get('frequency')
        if not frequency:
            return Response(
                {"error": "frequency parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        plans = service.get_by_frequency(frequency)
        
        page = self.paginate_queryset(plans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get active maintenance plans.
        """
        service = self.get_service()
        plans = service.get_active_plans()
        
        page = self.paginate_queryset(plans)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(plans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def generate_tasks(self, request, pk=None):
        """
        Generate maintenance tasks for this plan.
        """
        assignee_id = request.data.get('assignee_id')
        due_date = request.data.get('due_date')
        
        if due_date:
            try:
                due_date = parse_date(due_date)
            except ValueError:
                return Response(
                    {"error": "Invalid date format for due_date. Use YYYY-MM-DD format."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        service = self.get_service()
        task = service.generate_task(self.get_object(), assignee_id, due_date)
        
        return Response({
            'message': 'Maintenance task created successfully',
            'task_id': task.id
        }) 