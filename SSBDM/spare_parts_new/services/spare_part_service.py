from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from core.services.base_service import BaseService
from ..models import SparePart, SparePartTransaction


class SparePartService(BaseService[SparePart]):
    """
    Service class for SparePart entity.
    Implements business logic for spare part management.
    """
    model_class = SparePart
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related('category')
    
    def search(self, query):
        """
        Search for spare parts based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered spare parts
        """
        return self.get_queryset().filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(manufacturer__icontains=query) |
            Q(supplier__icontains=query) |
            Q(supplier_reference__icontains=query)
        )
    
    def get_low_stock(self):
        """
        Get spare parts with low stock.
        
        Returns:
            QuerySet: Spare parts with low stock
        """
        return self.get_queryset().filter(
            current_stock__lt=models.F('minimum_stock')
        ).order_by('current_stock')
    
    def get_out_of_stock(self):
        """
        Get spare parts that are out of stock.
        
        Returns:
            QuerySet: Out of stock spare parts
        """
        return self.get_queryset().filter(current_stock=0)
    
    def get_by_category(self, category_id):
        """
        Get spare parts in a specific category.
        
        Args:
            category_id: Category ID
            
        Returns:
            QuerySet: Spare parts in specified category
        """
        return self.get_queryset().filter(category_id=category_id)
    
    def get_by_status(self, status):
        """
        Get spare parts by stock status.
        
        Args:
            status (str): Stock status
            
        Returns:
            QuerySet: Spare parts with specified status
        """
        if status == 'low_stock':
            return self.get_low_stock()
        elif status == 'out_of_stock':
            return self.get_out_of_stock()
        else:
            return self.get_queryset().filter(current_stock__gte=models.F('minimum_stock'))
    
    def get_recent_transactions(self, days=30):
        """
        Get spare parts with recent transactions.
        
        Args:
            days (int): Number of days in the past
            
        Returns:
            QuerySet: Spare parts with recent transactions
        """
        start_date = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(
            transactions__date__gte=start_date
        ).distinct()
    
    def get_spare_part_statistics(self):
        """
        Get statistics about spare parts.
        
        Returns:
            dict: Spare part statistics
        """
        total = self.get_queryset().count()
        low_stock = self.get_low_stock().count()
        out_of_stock = self.get_out_of_stock().count()
        
        # Total inventory value
        total_value = self.get_queryset().aggregate(
            total_value=Sum(models.F('price') * models.F('current_stock'))
        )['total_value'] or 0
        
        # Average stock levels
        avg_stock = self.get_queryset().aggregate(
            avg_stock=Avg('current_stock')
        )['avg_stock'] or 0
        
        # Categories with most spare parts
        category_stats = (
            self.get_queryset()
            .values('category__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return {
            'total': total,
            'low_stock': low_stock,
            'out_of_stock': out_of_stock,
            'total_value': total_value,
            'avg_stock': avg_stock,
            'category_stats': list(category_stats),
        } 