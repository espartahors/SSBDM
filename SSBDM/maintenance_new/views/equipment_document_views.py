from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from ..models import EquipmentDocument
from ..serializers import EquipmentDocumentSerializer, EquipmentDocumentDetailSerializer
from ..services import DocumentService
from ..permissions import DocumentPermission


class EquipmentDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for equipment documents.
    
    Provides CRUD operations and additional actions:
    - search
    - by_equipment
    - by_document_type
    - by_date_range
    - recent
    """
    queryset = EquipmentDocument.objects.all()
    serializer_class = EquipmentDocumentSerializer
    permission_classes = [DocumentPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'document_type', 'date_added']
    search_fields = ['title', 'description', 'file_name']
    ordering_fields = ['date_added', 'date_updated', 'title']
    ordering = ['-date_added']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return EquipmentDocumentDetailSerializer
        return EquipmentDocumentSerializer
    
    def get_service(self):
        """Get document service instance."""
        return DocumentService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new document using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        document = service.create(**data)
        serializer.instance = document
    
    def perform_update(self, serializer):
        """Update document using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        document = service.update(serializer.instance, **data)
        serializer.instance = document
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for documents based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        documents = service.search(query)
        page = self.paginate_queryset(documents)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_equipment(self, request):
        """
        Get documents for a specific equipment.
        """
        equipment_id = request.query_params.get('equipment_id')
        if not equipment_id:
            return Response(
                {"error": "equipment_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        documents = service.get_by_equipment(equipment_id)
        
        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_document_type(self, request):
        """
        Get documents by type.
        """
        doc_type = request.query_params.get('type')
        if not doc_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        documents = service.get_by_document_type(doc_type)
        
        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """
        Get documents within a date range.
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
        documents = service.get_by_date_range(start_date, end_date)
        
        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent documents.
        """
        days = int(request.query_params.get('days', 30))
        service = self.get_service()
        documents = service.get_recent_documents(days=days)
        
        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data) 