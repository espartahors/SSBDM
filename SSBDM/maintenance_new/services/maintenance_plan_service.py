from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from core.services.base_service import BaseService
from ..models import MaintenancePlan, MaintenanceLog


class MaintenancePlanService(BaseService[MaintenancePlan]):
    """
    Service class for MaintenancePlan entity.
    Implements business logic for maintenance plan management.
    """
    model_class = MaintenancePlan
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related(
            'equipment',
            'created_by',
            'updated_by'
        )
    
    def search(self, query):
        """
        Search for maintenance plans based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered maintenance plans
        """
        return self.get_queryset().filter(
            Q(code__icontains=query) |
            Q(name__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(equipment__code__icontains=query) |
            Q(equipment__name__icontains=query)
        )
    
    def get_by_equipment(self, equipment_id):
        """
        Get maintenance plans for a specific equipment.
        
        Args:
            equipment_id: Equipment ID
            
        Returns:
            QuerySet: Maintenance plans for specified equipment
        """
        return self.get_queryset().filter(equipment_id=equipment_id)
    
    def get_by_type(self, maintenance_type):
        """
        Get maintenance plans by type.
        
        Args:
            maintenance_type (str): Maintenance type
            
        Returns:
            QuerySet: Maintenance plans of specified type
        """
        return self.get_queryset().filter(maintenance_type=maintenance_type)
    
    def get_active_plans(self):
        """
        Get active maintenance plans.
        
        Returns:
            QuerySet: Active maintenance plans
        """
        return self.get_queryset().filter(is_active=True)
    
    def get_due_soon(self, days=7):
        """
        Get maintenance plans due within a certain number of days.
        
        Args:
            days (int): Number of days in the future
            
        Returns:
            QuerySet: Maintenance plans due soon
        """
        today = timezone.now().date()
        future = today + timedelta(days=days)
        return self.get_queryset().filter(
            next_due__range=[today, future],
            is_active=True
        )
    
    def get_overdue(self):
        """
        Get overdue maintenance plans.
        
        Returns:
            QuerySet: Overdue maintenance plans
        """
        today = timezone.now().date()
        return self.get_queryset().filter(
            next_due__lt=today,
            is_active=True
        )
    
    def execute_plan(self, plan_id, **log_data):
        """
        Execute a maintenance plan and create a maintenance log.
        
        Args:
            plan_id: Maintenance plan ID
            **log_data: Data for maintenance log
            
        Returns:
            MaintenanceLog: Created maintenance log
        """
        plan = self.get_by_id(plan_id)
        
        # Create maintenance log
        from ..services import MaintenanceLogService
        log_service = MaintenanceLogService(user=self.user)
        
        # Prepare log data
        log_data.setdefault('equipment_id', plan.equipment_id)
        log_data.setdefault('maintenance_type', plan.maintenance_type)
        log_data.setdefault('title', f"Plan: {plan.title}")
        log_data.setdefault('description', plan.description)
        log_data.setdefault('date', timezone.now().date())
        log_data.setdefault('duration', plan.estimated_duration)
        
        # Create log
        log = log_service.create(**log_data)
        
        # Update plan
        plan.last_executed = log_data['date']
        plan.next_due = plan.calculate_next_due()
        plan.save()
        
        return log
    
    def get_plan_statistics(self):
        """
        Get statistics about maintenance plans.
        
        Returns:
            dict: Maintenance plan statistics
        """
        today = timezone.now().date()
        
        # Total plans
        total = self.get_queryset().count()
        active = self.get_active_plans().count()
        
        # Plans by type
        type_counts = dict(
            self.get_queryset()
            .values('maintenance_type')
            .annotate(count=Count('id'))
            .values_list('maintenance_type', 'count')
        )
        
        # Plans by frequency
        frequency_counts = dict(
            self.get_queryset()
            .values('frequency')
            .annotate(count=Count('id'))
            .values_list('frequency', 'count')
        )
        
        # Overdue plans
        overdue_count = self.get_overdue().count()
        
        # Due soon plans (next 7 days)
        due_soon_count = self.get_due_soon(days=7).count()
        
        # Equipment with most plans
        equipment_stats = list(
            self.get_queryset()
            .values('equipment__code', 'equipment__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        return {
            'total': total,
            'active': active,
            'type_counts': type_counts,
            'frequency_counts': frequency_counts,
            'overdue_count': overdue_count,
            'due_soon_count': due_soon_count,
            'equipment_stats': equipment_stats,
        } 