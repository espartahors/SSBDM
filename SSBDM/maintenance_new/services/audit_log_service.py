from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from core.services.base_service import BaseService
from ..models import AuditLog


class AuditLogService(BaseService[AuditLog]):
    """
    Service class for AuditLog entity.
    Implements business logic for audit log management.
    """
    model_class = AuditLog
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related('user')
    
    def search(self, query):
        """
        Search for audit logs based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered audit logs
        """
        return self.get_queryset().filter(
            Q(model_name__icontains=query) |
            Q(details__icontains=query) |
            Q(user__username__icontains=query)
        )
    
    def get_by_model(self, model_name):
        """
        Get audit logs for a specific model.
        
        Args:
            model_name (str): Model name
            
        Returns:
            QuerySet: Audit logs for specified model
        """
        return self.get_queryset().filter(model_name=model_name)
    
    def get_by_action(self, action):
        """
        Get audit logs by action.
        
        Args:
            action (str): Action type
            
        Returns:
            QuerySet: Audit logs with specified action
        """
        return self.get_queryset().filter(action=action)
    
    def get_by_user(self, user_id):
        """
        Get audit logs for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            QuerySet: Audit logs for specified user
        """
        return self.get_queryset().filter(user_id=user_id)
    
    def get_by_object(self, model_name, object_id):
        """
        Get audit logs for a specific object.
        
        Args:
            model_name (str): Model name
            object_id: Object ID
            
        Returns:
            QuerySet: Audit logs for specified object
        """
        return self.get_queryset().filter(
            model_name=model_name,
            object_id=object_id
        )
    
    def get_recent_logs(self, days=7):
        """
        Get recent audit logs.
        
        Args:
            days (int): Number of days in the past
            
        Returns:
            QuerySet: Recent audit logs
        """
        start_date = timezone.now() - timedelta(days=days)
        return self.get_queryset().filter(timestamp__gte=start_date)
    
    def log_action(self, action, model_name, object_id=None, details=''):
        """
        Log a user action.
        
        Args:
            action (str): Action type
            model_name (str): Model name
            object_id (optional): Object ID
            details (str, optional): Additional details
            
        Returns:
            AuditLog: Created audit log
        """
        return self.create(
            user=self.user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            details=details
        )
    
    def get_audit_statistics(self, days=30):
        """
        Get statistics about audit logs.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            dict: Audit log statistics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        # Total logs
        total = self.get_queryset().filter(timestamp__gte=start_date).count()
        
        # Logs by action
        action_counts = dict(
            self.get_queryset()
            .filter(timestamp__gte=start_date)
            .values('action')
            .annotate(count=Count('id'))
            .values_list('action', 'count')
        )
        
        # Logs by model
        model_counts = dict(
            self.get_queryset()
            .filter(timestamp__gte=start_date)
            .values('model_name')
            .annotate(count=Count('id'))
            .values_list('model_name', 'count')
        )
        
        # Most active users
        user_stats = list(
            self.get_queryset()
            .filter(timestamp__gte=start_date, user__isnull=False)
            .values('user__username')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        # Action trends by day
        from django.db.models.functions import TruncDay
        
        action_trends = list(
            self.get_queryset()
            .filter(timestamp__gte=start_date)
            .annotate(day=TruncDay('timestamp'))
            .values('day', 'action')
            .annotate(count=Count('id'))
            .order_by('day', 'action')
        )
        
        return {
            'total': total,
            'action_counts': action_counts,
            'model_counts': model_counts,
            'user_stats': user_stats,
            'action_trends': action_trends,
        } 