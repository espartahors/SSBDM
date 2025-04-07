from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from core.models import BaseModel, NotesMixin
from core.utils.constants import MAINTENANCE_TYPES, MAINTENANCE_RESULTS
from equipment_new.models import Equipment


class MaintenanceLog(BaseModel, NotesMixin):
    """
    Model for maintenance logs with improved structure.
    Records maintenance activities performed on equipment.
    """
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        related_name='maintenance_logs'
    )
    maintenance_type = models.CharField(
        max_length=20, 
        choices=MAINTENANCE_TYPES
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    duration = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text='Duration in hours'
    )
    technicians = models.ManyToManyField(
        User, 
        related_name='maintenance_work'
    )
    observations = models.TextField(blank=True)
    maintenance_result = models.CharField(
        max_length=20, 
        choices=MAINTENANCE_RESULTS, 
        blank=True, 
        null=True
    )
    result_description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date']
        permissions = [
            ('can_manage_maintenance', 'Can manage maintenance logs'),
        ]
    
    def __str__(self):
        return f"{self.equipment.code} - {self.title} ({self.date})"
        
    def get_absolute_url(self):
        return reverse('maintenance:log_detail', kwargs={'pk': self.pk}) 