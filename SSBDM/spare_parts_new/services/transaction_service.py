from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from core.services.base_service import BaseService
from ..models import SparePartTransaction, SparePart


class TransactionService(BaseService[SparePartTransaction]):
    """
    Service class for SparePartTransaction entity.
    Implements business logic for transaction management.
    """
    model_class = SparePartTransaction
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related(
            'spare_part',
            'equipment',
            'created_by'
        )
    
    def get_by_spare_part(self, spare_part_id):
        """
        Get transactions for a specific spare part.
        
        Args:
            spare_part_id: Spare part ID
            
        Returns:
            QuerySet: Transactions for specified spare part
        """
        return self.get_queryset().filter(spare_part_id=spare_part_id)
    
    def get_by_equipment(self, equipment_id):
        """
        Get transactions for a specific equipment.
        
        Args:
            equipment_id: Equipment ID
            
        Returns:
            QuerySet: Transactions for specified equipment
        """
        return self.get_queryset().filter(equipment_id=equipment_id)
    
    def get_by_type(self, transaction_type):
        """
        Get transactions by type.
        
        Args:
            transaction_type (str): Transaction type
            
        Returns:
            QuerySet: Transactions of specified type
        """
        return self.get_queryset().filter(transaction_type=transaction_type)
    
    def get_recent_transactions(self, days=30):
        """
        Get recent transactions.
        
        Args:
            days (int): Number of days in the past
            
        Returns:
            QuerySet: Recent transactions
        """
        start_date = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(date__gte=start_date)
    
    def get_transaction_statistics(self, days=30):
        """
        Get statistics about transactions.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            dict: Transaction statistics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Total transactions
        total = self.get_queryset().filter(date__gte=start_date).count()
        
        # Transactions by type
        type_counts = dict(
            self.get_queryset()
            .filter(date__gte=start_date)
            .values('transaction_type')
            .annotate(count=Count('id'))
            .values_list('transaction_type', 'count')
        )
        
        # Total quantity by type
        quantity_by_type = dict(
            self.get_queryset()
            .filter(date__gte=start_date)
            .values('transaction_type')
            .annotate(total=Sum('quantity'))
            .values_list('transaction_type', 'total')
        )
        
        # Total value by type
        value_by_type = dict(
            self.get_queryset()
            .filter(date__gte=start_date)
            .values('transaction_type')
            .annotate(total=Sum(models.F('quantity') * models.F('unit_price')))
            .values_list('transaction_type', 'total')
        )
        
        # Most used spare parts
        top_spare_parts = list(
            self.get_queryset()
            .filter(date__gte=start_date)
            .values('spare_part__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return {
            'total': total,
            'type_counts': type_counts,
            'quantity_by_type': quantity_by_type,
            'value_by_type': value_by_type,
            'top_spare_parts': top_spare_parts,
        }
    
    def create_transaction(self, **data):
        """
        Create a new transaction and update stock levels.
        
        Args:
            **data: Transaction data
            
        Returns:
            SparePartTransaction: Created transaction
        """
        transaction = self.create(**data)
        return transaction 