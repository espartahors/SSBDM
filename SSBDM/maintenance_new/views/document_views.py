from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from ..models import EquipmentDocument
from ..serializers import EquipmentDocumentSerializer, EquipmentDocumentDetailSerializer
from ..services import DocumentService


class EquipmentDocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for equipment documents.
    
    Provides CRUD operations and additional actions:
    - search
    - by_equipment
    - by_type
    - statistics
    """
    queryset = EquipmentDocument.objects.all()
    serializer_class = EquipmentDocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'document_type', 'upload_date']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'upload_date', 'created_at', 'updated_at']
    ordering = ['title']
    parser_classes = [MultiPartParser, FormParser]
    
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
    def by_type(self, request):
        """
        Get documents by type.
        """
        document_type = request.query_params.get('type')
        if not document_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        documents = service.get_by_type(document_type)
        
        page = self.paginate_queryset(documents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(documents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get document statistics.
        """
        service = self.get_service()
        stats = service.get_document_statistics()
        return Response(stats) 