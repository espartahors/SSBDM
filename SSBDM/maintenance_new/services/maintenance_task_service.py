from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from core.services.base_service import BaseService
from ..models import MaintenanceTask


class MaintenanceTaskService(BaseService[MaintenanceTask]):
    """
    Service class for MaintenanceTask entity.
    Implements business logic for maintenance task management.
    """
    model_class = MaintenanceTask
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related(
            'maintenance_log',
            'maintenance_log__equipment',
            'assigned_to',
            'created_by',
            'updated_by'
        )
    
    def search(self, query):
        """
        Search for maintenance tasks based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered maintenance tasks
        """
        return self.get_queryset().filter(
            Q(description__icontains=query) |
            Q(notes__icontains=query) |
            Q(maintenance_log__title__icontains=query) |
            Q(maintenance_log__equipment__code__icontains=query) |
            Q(maintenance_log__equipment__name__icontains=query)
        )
    
    def get_by_log(self, log_id):
        """
        Get tasks for a specific maintenance log.
        
        Args:
            log_id: Maintenance log ID
            
        Returns:
            QuerySet: Tasks for specified log
        """
        return self.get_queryset().filter(maintenance_log_id=log_id)
    
    def get_by_equipment(self, equipment_id):
        """
        Get tasks for a specific equipment.
        
        Args:
            equipment_id: Equipment ID
            
        Returns:
            QuerySet: Tasks for specified equipment
        """
        return self.get_queryset().filter(maintenance_log__equipment_id=equipment_id)
    
    def get_by_status(self, status):
        """
        Get tasks by status.
        
        Args:
            status (str): Task status
            
        Returns:
            QuerySet: Tasks with specified status
        """
        return self.get_queryset().filter(status=status)
    
    def get_assigned_to_user(self, user_id):
        """
        Get tasks assigned to a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            QuerySet: Tasks assigned to specified user
        """
        return self.get_queryset().filter(assigned_to_id=user_id)
    
    def get_overdue_tasks(self):
        """
        Get overdue tasks (due date in the past and not completed).
        
        Returns:
            QuerySet: Overdue tasks
        """
        today = timezone.now().date()
        return self.get_queryset().filter(
            due_date__lt=today,
            status__in=['pending', 'in_progress']
        )
    
    def get_upcoming_tasks(self, days=7):
        """
        Get upcoming tasks (due in the next X days).
        
        Args:
            days (int): Number of days in the future
            
        Returns:
            QuerySet: Upcoming tasks
        """
        today = timezone.now().date()
        future = today + timedelta(days=days)
        return self.get_queryset().filter(
            due_date__range=[today, future],
            status__in=['pending', 'in_progress']
        )
    
    def get_task_statistics(self):
        """
        Get statistics about tasks.
        
        Returns:
            dict: Task statistics
        """
        total = self.get_queryset().count()
        
        # Tasks by status
        status_counts = dict(
            self.get_queryset()
            .values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )
        
        # Overdue tasks
        overdue_count = self.get_overdue_tasks().count()
        
        # Upcoming tasks (next 7 days)
        upcoming_count = self.get_upcoming_tasks(days=7).count()
        
        # Tasks by assignee
        assignee_stats = list(
            self.get_queryset()
            .filter(assigned_to__isnull=False)
            .values('assigned_to__username')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return {
            'total': total,
            'status_counts': status_counts,
            'overdue_count': overdue_count,
            'upcoming_count': upcoming_count,
            'assignee_stats': assignee_stats,
        } 