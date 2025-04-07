from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date
from ..models import SparePartTransaction
from ..serializers import SparePartTransactionSerializer, SparePartTransactionDetailSerializer
from ..services import TransactionService
from ..permissions import TransactionPermission


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for inventory transactions.
    
    Provides CRUD operations and additional actions:
    - search
    - by_spare_part
    - by_transaction_type
    - by_date_range
    - recent
    """
    queryset = SparePartTransaction.objects.all()
    serializer_class = SparePartTransactionSerializer
    permission_classes = [TransactionPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['spare_part', 'transaction_type', 'transaction_date']
    search_fields = ['notes', 'reference_number']
    ordering_fields = ['transaction_date', 'spare_part', 'quantity']
    ordering = ['-transaction_date']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return SparePartTransactionDetailSerializer
        return SparePartTransactionSerializer
    
    def get_service(self):
        """Get transaction service instance."""
        return TransactionService(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create new transaction using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        transaction = service.create(**data)
        serializer.instance = transaction
    
    def perform_update(self, serializer):
        """Update transaction using service."""
        service = self.get_service()
        data = serializer.validated_data.copy()
        transaction = service.update(serializer.instance, **data)
        serializer.instance = transaction
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Search for transactions based on query parameter.
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {"error": "Search query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        transactions = service.search(query)
        page = self.paginate_queryset(transactions)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_spare_part(self, request):
        """
        Get transactions for a specific spare part.
        """
        spare_part_id = request.query_params.get('spare_part_id')
        if not spare_part_id:
            return Response(
                {"error": "spare_part_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        transactions = service.get_by_spare_part(spare_part_id)
        
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_transaction_type(self, request):
        """
        Get transactions by type.
        """
        transaction_type = request.query_params.get('type')
        if not transaction_type:
            return Response(
                {"error": "type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        transactions = service.get_by_transaction_type(transaction_type)
        
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """
        Get transactions within a date range.
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
        transactions = service.get_by_date_range(start_date, end_date)
        
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent transactions.
        """
        days = int(request.query_params.get('days', 7))
        service = self.get_service()
        transactions = service.get_recent(days=days)
        
        page = self.paginate_queryset(transactions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data) 