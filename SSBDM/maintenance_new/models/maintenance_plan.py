from django.db import models
from django.urls import reverse
from django.utils import timezone
from core.models import BaseModel, NotesMixin, CodeNameMixin
from core.utils.constants import MAINTENANCE_TYPES, FREQUENCY_CHOICES
from equipment_new.models import Equipment


class MaintenancePlan(BaseModel, CodeNameMixin, NotesMixin):
    """
    Model for maintenance plans with improved structure.
    Defines scheduled maintenance activities for equipment.
    """
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        related_name='maintenance_plans'
    )
    maintenance_type = models.CharField(
        max_length=20, 
        choices=MAINTENANCE_TYPES
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    frequency = models.CharField(
        max_length=20, 
        choices=FREQUENCY_CHOICES
    )
    frequency_value = models.PositiveIntegerField(
        help_text="Value for frequency (e.g., 3 for every 3 days if frequency is 'days')"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    estimated_duration = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text='Estimated duration in hours'
    )
    is_active = models.BooleanField(default=True)
    last_executed = models.DateField(null=True, blank=True)
    next_due = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['equipment', 'title']
        permissions = [
            ('can_manage_maintenance_plans', 'Can manage maintenance plans'),
        ]
    
    def __str__(self):
        return f"{self.equipment.code} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('maintenance:plan_detail', kwargs={'pk': self.pk})
    
    def calculate_next_due(self):
        """Calculate next due date based on frequency and last execution."""
        base_date = self.last_executed or self.start_date
        
        if self.frequency == 'days':
            return base_date + timezone.timedelta(days=self.frequency_value)
        elif self.frequency == 'weeks':
            return base_date + timezone.timedelta(weeks=self.frequency_value)
        elif self.frequency == 'months':
            # Add months (approximately)
            year = base_date.year + ((base_date.month + self.frequency_value - 1) // 12)
            month = ((base_date.month + self.frequency_value - 1) % 12) + 1
            day = min(base_date.day, self._days_in_month(year, month))
            return timezone.datetime(year, month, day).date()
        elif self.frequency == 'years':
            # Add years
            year = base_date.year + self.frequency_value
            month = base_date.month
            day = min(base_date.day, self._days_in_month(year, month))
            return timezone.datetime(year, month, day).date()
        return base_date
    
    def _days_in_month(self, year, month):
        """Helper method to get days in a month."""
        if month == 2:
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 29
            return 28
        elif month in [4, 6, 9, 11]:
            return 30
        return 31
    
    def save(self, *args, **kwargs):
        """Override save to calculate next due date."""
        if not self.next_due or self._state.adding:
            self.next_due = self.calculate_next_due()
        super().save(*args, **kwargs) 