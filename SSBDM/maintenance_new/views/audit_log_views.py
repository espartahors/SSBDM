from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from ..models import AuditLog
from ..serializers import AuditLogSerializer, AuditLogDetailSerializer
from ..services import AuditLogService
from ..permissions import AuditLogPermission


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for audit logs (read-only).
    
    Provides list and retrieve operations and additional actions:
    - search
    - by_model
    - by_action
    - by_user
    - by_date_range
    - recent
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [AuditLogPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['model_name', 'action', 'user']
    search_fields = ['model_name', 'details']
    ordering_fields = ['timestamp', 'model_name', 'action']
    ordering = ['-timestamp']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return AuditLogDetailSerializer
        return AuditLogSerializer
    
    def get_service(self):
        """Get audit log service instance."""
        return AuditLogService(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for audit logs based on query parameter.
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
    def by_model(self, request):
        """
        Get audit logs for a specific model.
        """
        model_name = request.query_params.get('model')
        if not model_name:
            return Response(
                {"error": "model parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.get_by_model(model_name)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_action(self, request):
        """
        Get audit logs by action type.
        """
        action = request.query_params.get('action')
        if not action:
            return Response(
                {"error": "action parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.get_by_action(action)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """
        Get audit logs by user.
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "user_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        logs = service.get_by_user(user_id)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """
        Get audit logs within a date range.
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
    def recent(self, request):
        """
        Get recent audit logs.
        """
        days = int(request.query_params.get('days', 7))
        service = self.get_service()
        logs = service.get_recent(days=days)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data) 