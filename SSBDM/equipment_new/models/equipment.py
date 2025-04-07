from django.db import models
from django.urls import reverse
from django.utils import timezone
from core.models import BaseModel, CodeNameMixin, NotesMixin
from core.utils.constants import EQUIPMENT_STATUS_CHOICES, EQUIPMENT_TYPE_CHOICES


class Equipment(BaseModel, CodeNameMixin, NotesMixin):
    """
    Equipment or machinery model with improved structure.
    """
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES)
    area = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment_set')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    manufacturer = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EQUIPMENT_STATUS_CHOICES, default='operational')
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_expiration = models.DateField(null=True, blank=True)
    expected_lifetime = models.PositiveIntegerField(help_text="Expected lifetime in months", null=True, blank=True)
    is_critical = models.BooleanField(default=False, help_text="Indicates if this is critical equipment")
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_interval = models.PositiveIntegerField(help_text="Maintenance interval in days", null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Equipment'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['equipment_type']),
            models.Index(fields=['status']),
        ]
        permissions = [
            ('can_manage_equipment', 'Can manage equipment'),
        ]
    
    def get_absolute_url(self):
        """Get URL for equipment detail view."""
        return reverse('equipment:equipment_detail', kwargs={'pk': self.pk})

    @property
    def get_all_children(self):
        """Return all child equipment."""
        return Equipment.objects.filter(parent=self)
        
    @property
    def get_maintenance_status(self):
        """Return maintenance status based on dates."""
        if not self.next_maintenance_date:
            return "unknown"
        
        today = timezone.now().date()
        days_until = (self.next_maintenance_date - today).days
        
        if days_until < 0:
            return "overdue"
        elif days_until <= 7:
            return "due_soon"
        else:
            return "scheduled" 