from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from core.services.base_service import BaseService
from ..models import Equipment


class EquipmentService(BaseService[Equipment]):
    """
    Service class for Equipment entity.
    Implements business logic for equipment management.
    """
    model_class = Equipment
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related('area')
    
    def search(self, query):
        """
        Search for equipment based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered equipment
        """
        return self.get_queryset().filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(manufacturer__icontains=query) |
            Q(model__icontains=query) |
            Q(serial_number__icontains=query)
        )
    
    def get_upcoming_maintenance(self, days=30):
        """
        Get equipment with upcoming maintenance.
        
        Args:
            days (int): Number of days in the future
            
        Returns:
            QuerySet: Equipment with upcoming maintenance
        """
        today = timezone.now().date()
        future_date = today + timedelta(days=days)
        
        return self.get_queryset().filter(
            next_maintenance_date__gte=today,
            next_maintenance_date__lte=future_date
        ).order_by('next_maintenance_date')
    
    def get_overdue_maintenance(self):
        """
        Get equipment with overdue maintenance.
        
        Returns:
            QuerySet: Equipment with overdue maintenance
        """
        today = timezone.now().date()
        
        return self.get_queryset().filter(
            next_maintenance_date__lt=today
        ).order_by('next_maintenance_date')
    
    def get_critical_equipment(self):
        """
        Get critical equipment.
        
        Returns:
            QuerySet: Critical equipment
        """
        return self.get_queryset().filter(is_critical=True)
    
    def get_equipment_by_status(self, status):
        """
        Get equipment by status.
        
        Args:
            status (str): Equipment status
            
        Returns:
            QuerySet: Equipment with specified status
        """
        return self.get_queryset().filter(status=status)
    
    def get_equipment_by_type(self, equipment_type):
        """
        Get equipment by type.
        
        Args:
            equipment_type (str): Equipment type
            
        Returns:
            QuerySet: Equipment of specified type
        """
        return self.get_queryset().filter(equipment_type=equipment_type)
    
    def get_equipment_by_area(self, area_id):
        """
        Get equipment in a specific area.
        
        Args:
            area_id: Area ID
            
        Returns:
            QuerySet: Equipment in specified area
        """
        return self.get_queryset().filter(area_id=area_id)
    
    def schedule_maintenance(self, equipment, maintenance_date):
        """
        Schedule maintenance for equipment.
        
        Args:
            equipment: Equipment instance
            maintenance_date: Date for maintenance
            
        Returns:
            Equipment: Updated equipment
        """
        return self.update(
            equipment,
            next_maintenance_date=maintenance_date
        )
    
    def complete_maintenance(self, equipment):
        """
        Mark maintenance as completed and schedule next maintenance.
        
        Args:
            equipment: Equipment instance
            
        Returns:
            Equipment: Updated equipment
        """
        today = timezone.now().date()
        next_date = None
        
        if equipment.maintenance_interval:
            next_date = today + timedelta(days=equipment.maintenance_interval)
        
        return self.update(
            equipment,
            last_maintenance_date=today,
            next_maintenance_date=next_date,
            status='operational'
        )
    
    def get_equipment_statistics(self):
        """
        Get statistics about equipment.
        
        Returns:
            dict: Equipment statistics
        """
        total = self.get_queryset().count()
        status_counts = dict(
            self.get_queryset()
            .values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        type_counts = dict(
            self.get_queryset()
            .values('equipment_type')
            .annotate(count=Count('id'))
            .values_list('equipment_type', 'count')
        )
        
        critical_count = self.get_critical_equipment().count()
        maintenance_needed = self.get_overdue_maintenance().count()
        
        return {
            'total': total,
            'status_counts': status_counts,
            'type_counts': type_counts,
            'critical_count': critical_count,
            'maintenance_needed': maintenance_needed,
        } 