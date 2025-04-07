from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from ..models import MaintenanceTask
from ..serializers import MaintenanceTaskSerializer, MaintenanceTaskDetailSerializer
from ..services import MaintenanceTaskService
from ..permissions import TaskPermission


class MaintenanceTaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for maintenance tasks.
    
    Provides CRUD operations and additional actions:
    - search
    - by_assignee
    - by_equipment
    - by_status
    - by_priority
    - by_due_date
    - mark_complete
    - overdue
    """
    queryset = MaintenanceTask.objects.all()
    serializer_class = MaintenanceTaskSerializer
    permission_classes = [TaskPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assignee', 'equipment', 'status', 'priority', 'due_date']
    search_fields = ['title', 'description', 'notes']
    ordering_fields = ['due_date', 'created_at', 'updated_at', 'priority']
    ordering = ['due_date', '-priority']
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'retrieve':
            return MaintenanceTaskDetailSerializer
        return MaintenanceTaskSerializer
    
    def get_service(self):
        """Get maintenance task service instance."""
        return MaintenanceTaskService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new maintenance task using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        task = service.create(**data)
        serializer.instance = task
    
    def perform_update(self, serializer):
        """Update maintenance task using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        task = service.update(serializer.instance, **data)
        serializer.instance = task
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for maintenance tasks based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        tasks = service.search(query)
        page = self.paginate_queryset(tasks)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_assignee(self, request):
        """
        Get tasks assigned to a specific user.
        """
        assignee_id = request.query_params.get('assignee_id')
        if not assignee_id:
            return Response(
                {"error": "assignee_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        tasks = service.get_by_assignee(assignee_id)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_equipment(self, request):
        """
        Get tasks for a specific equipment.
        """
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {"error": "equipment_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        tasks = service.get_by_equipment(equipment_id)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get tasks by status.
        """
        status_value = request.query_params.get('status')
        if not status_value:
            return Response(
                {"error": "status parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        tasks = service.get_by_status(status_value)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_priority(self, request):
        """
        Get tasks by priority.
        """
        priority = request.query_params.get('priority')
        if not priority:
            return Response(
                {"error": "priority parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        tasks = service.get_by_priority(priority)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_due_date(self, request):
        """
        Get tasks by due date range.
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
        tasks = service.get_by_due_date_range(start_date, end_date)
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """
        Mark task as complete with optional notes.
        """
        notes = request.data.get('notes', '')
        
        service = self.get_service()
        task = service.mark_complete(self.get_object(), notes)
        
        serializer = MaintenanceTaskDetailSerializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue tasks.
        """
        service = self.get_service()
        tasks = service.get_overdue_tasks()
        
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data) 