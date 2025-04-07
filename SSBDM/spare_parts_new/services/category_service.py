from django.db.models import Q, Count
from core.services.base_service import BaseService
from ..models import Category, SparePart


class CategoryService(BaseService[Category]):
    """
    Service class for Category entity.
    Implements business logic for category management.
    """
    model_class = Category
    
    def get_queryset(self):
        """Return the base queryset."""
        return super().get_queryset()
    
    def search(self, query):
        """
        Search for categories based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered categories
        """
        return self.get_queryset().filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    def get_categories_with_spare_parts_count(self):
        """
        Get categories with spare parts count.
        
        Returns:
            QuerySet: Categories with spare parts count
        """
        return self.get_queryset().annotate(
            spare_parts_count=Count('spare_parts')
        )
    
    def get_categories_with_low_stock(self):
        """
        Get categories with spare parts that have low stock.
        
        Returns:
            QuerySet: Categories with low stock items
        """
        return self.get_queryset().filter(
            spare_parts__current_stock__lt=models.F('spare_parts__minimum_stock')
        ).distinct()
    
    def get_categories_with_out_of_stock(self):
        """
        Get categories with spare parts that are out of stock.
        
        Returns:
            QuerySet: Categories with out of stock items
        """
        return self.get_queryset().filter(
            spare_parts__current_stock=0
        ).distinct()
    
    def get_category_statistics(self):
        """
        Get statistics about categories.
        
        Returns:
            dict: Category statistics
        """
        total = self.get_queryset().count()
        
        categories_with_spare_parts = self.get_categories_with_spare_parts_count()
        total_spare_parts = sum(c.spare_parts_count for c in categories_with_spare_parts)
        
        # Categories with most spare parts
        top_categories = list(
            categories_with_spare_parts
            .order_by('-spare_parts_count')
            .values('id', 'name', 'spare_parts_count')[:5]
        )
        
        # Categories with low stock
        low_stock_categories_count = self.get_categories_with_low_stock().count()
        
        # Categories with out of stock
        out_of_stock_categories_count = self.get_categories_with_out_of_stock().count()
        
        return {
            'total_categories': total,
            'total_spare_parts': total_spare_parts,
            'top_categories': top_categories,
            'low_stock_categories_count': low_stock_categories_count,
            'out_of_stock_categories_count': out_of_stock_categories_count,
        } 