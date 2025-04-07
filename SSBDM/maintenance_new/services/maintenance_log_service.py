from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from core.services.base_service import BaseService
from ..models import MaintenanceLog


class MaintenanceLogService(BaseService[MaintenanceLog]):
    """
    Service class for MaintenanceLog entity.
    Implements business logic for maintenance log management.
    """
    model_class = MaintenanceLog
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related(
            'equipment',
            'created_by',
            'updated_by'
        ).prefetch_related('technicians', 'tasks')
    
    def search(self, query):
        """
        Search for maintenance logs based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered maintenance logs
        """
        return self.get_queryset().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(observations__icontains=query) |
            Q(result_description__icontains=query) |
            Q(equipment__code__icontains=query) |
            Q(equipment__name__icontains=query)
        )
    
    def get_by_equipment(self, equipment_id):
        """
        Get maintenance logs for a specific equipment.
        
        Args:
            equipment_id: Equipment ID
            
        Returns:
            QuerySet: Maintenance logs for specified equipment
        """
        return self.get_queryset().filter(equipment_id=equipment_id)
    
    def get_by_type(self, maintenance_type):
        """
        Get maintenance logs by type.
        
        Args:
            maintenance_type (str): Maintenance type
            
        Returns:
            QuerySet: Maintenance logs of specified type
        """
        return self.get_queryset().filter(maintenance_type=maintenance_type)
    
    def get_by_date_range(self, start_date, end_date):
        """
        Get maintenance logs within a date range.
        
        Args:
            start_date (date): Start date
            end_date (date): End date
            
        Returns:
            QuerySet: Maintenance logs within date range
        """
        return self.get_queryset().filter(date__range=[start_date, end_date])
    
    def get_by_result(self, result):
        """
        Get maintenance logs by result.
        
        Args:
            result (str): Maintenance result
            
        Returns:
            QuerySet: Maintenance logs with specified result
        """
        return self.get_queryset().filter(maintenance_result=result)
    
    def get_recent_logs(self, days=30):
        """
        Get recent maintenance logs.
        
        Args:
            days (int): Number of days in the past
            
        Returns:
            QuerySet: Recent maintenance logs
        """
        start_date = timezone.now().date() - timedelta(days=days)
        return self.get_queryset().filter(date__gte=start_date)
    
    def get_statistics(self, days=30):
        """
        Get statistics about maintenance logs.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            dict: Maintenance log statistics
        """
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Total logs
        total = self.get_queryset().filter(date__gte=start_date).count()
        
        # Logs by type
        type_counts = dict(
            self.get_queryset()
            .filter(date__gte=start_date)
            .values('maintenance_type')
            .annotate(count=Count('id'))
            .values_list('maintenance_type', 'count')
        )
        
        # Logs by result
        result_counts = dict(
            self.get_queryset()
            .filter(date__gte=start_date)
            .exclude(maintenance_result__isnull=True)
            .values('maintenance_result')
            .annotate(count=Count('id'))
            .values_list('maintenance_result', 'count')
        )
        
        # Average duration
        avg_duration = self.get_queryset().filter(date__gte=start_date).aggregate(
            avg_duration=Avg('duration')
        )['avg_duration'] or 0
        
        # Total duration
        total_duration = self.get_queryset().filter(date__gte=start_date).aggregate(
            total_duration=Sum('duration')
        )['total_duration'] or 0
        
        # Equipment with most maintenance
        top_equipment = list(
            self.get_queryset()
            .filter(date__gte=start_date)
            .values('equipment__code', 'equipment__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return {
            'total': total,
            'type_counts': type_counts,
            'result_counts': result_counts,
            'avg_duration': avg_duration,
            'total_duration': total_duration,
            'top_equipment': top_equipment,
        } 