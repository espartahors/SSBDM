from django.db.models import Q, Count
from core.services.base_service import BaseService
from ..models import Area, Equipment


class AreaService(BaseService[Area]):
    """
    Service class for Area entity.
    Implements business logic for area management.
    """
    model_class = Area
    
    def get_queryset(self):
        """Return the base queryset."""
        return super().get_queryset()
    
    def search(self, query):
        """
        Search for areas based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered areas
        """
        return self.get_queryset().filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    
    def get_areas_with_equipment_count(self):
        """
        Get areas with equipment count.
        
        Returns:
            QuerySet: Areas with equipment count
        """
        return self.get_queryset().annotate(
            equipment_count=Count('equipment_set')
        )
    
    def get_areas_with_critical_equipment(self):
        """
        Get areas with critical equipment.
        
        Returns:
            QuerySet: Areas with critical equipment
        """
        return self.get_queryset().filter(
            equipment_set__is_critical=True
        ).distinct()
    
    def get_areas_with_maintenance_needed(self):
        """
        Get areas with equipment that needs maintenance.
        
        Returns:
            QuerySet: Areas with maintenance needed
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        return self.get_queryset().filter(
            equipment_set__next_maintenance_date__lt=today
        ).distinct()
    
    def get_area_statistics(self):
        """
        Get statistics about areas.
        
        Returns:
            dict: Area statistics
        """
        total = self.get_queryset().count()
        
        areas_with_equipment = self.get_areas_with_equipment_count()
        total_equipment = sum(a.equipment_count for a in areas_with_equipment)
        
        # Areas with most equipment
        top_areas = list(
            areas_with_equipment
            .order_by('-equipment_count')
            .values('id', 'name', 'equipment_count')[:5]
        )
        
        # Areas with critical equipment
        critical_areas_count = self.get_areas_with_critical_equipment().count()
        
        # Areas needing maintenance
        maintenance_areas_count = self.get_areas_with_maintenance_needed().count()
        
        return {
            'total_areas': total,
            'total_equipment': total_equipment,
            'top_areas': top_areas,
            'critical_areas_count': critical_areas_count,
            'maintenance_areas_count': maintenance_areas_count,
        } 