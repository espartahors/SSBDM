from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import BaseModel
from core.utils.constants import ACTION_CHOICES


class AuditLog(BaseModel):
    """
    Model for audit logs with improved structure.
    Tracks user actions across the system.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    action = models.CharField(
        max_length=10, 
        choices=ACTION_CHOICES
    )
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        permissions = [
            ('can_view_audit_logs', 'Can view audit logs'),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.model_name} - {self.timestamp}" 