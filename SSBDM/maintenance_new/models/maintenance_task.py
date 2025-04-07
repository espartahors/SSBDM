from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel, NotesMixin
from core.utils.constants import TASK_STATUS_CHOICES
from .maintenance_log import MaintenanceLog


class MaintenanceTask(BaseModel, NotesMixin):
    """
    Model for maintenance tasks with improved structure.
    Tasks are individual steps or actions within a maintenance log.
    """
    maintenance_log = models.ForeignKey(
        MaintenanceLog, 
        on_delete=models.CASCADE, 
        related_name='tasks'
    )
    description = models.TextField()
    status = models.CharField(
        max_length=20, 
        choices=TASK_STATUS_CHOICES, 
        default='pending'
    )
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='assigned_tasks'
    )
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-due_date']
        permissions = [
            ('can_manage_tasks', 'Can manage maintenance tasks'),
        ]
    
    def __str__(self):
        return f"Task for {self.maintenance_log.equipment.code} - {self.description[:50]}"
    
    def is_overdue(self):
        """Check if task is overdue."""
        if self.status != 'completed' and self.due_date < models.functions.Now().date():
            return True
        return False 