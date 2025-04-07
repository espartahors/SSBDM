from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
import uuid

# Choices
STATUS_CHOICES = (
    ('operational', 'Operational'),
    ('maintenance', 'Under Maintenance'),
    ('out_of_service', 'Out of Service'),
    ('retired', 'Retired'),
)

EQUIPMENT_TYPE_CHOICES = (
    ('machine', 'Machine'),
    ('tool', 'Tool'),
    ('vehicle', 'Vehicle'),
    ('instrument', 'Instrument'),
    ('component', 'Component'),
    ('system', 'System'),
    ('assembly', 'Assembly'),
    ('other', 'Other'),
)

class Area(MPTTModel):
    """Plant area or section"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('equipment:area_detail', kwargs={'pk': self.pk})

    class MPTTMeta:
        order_insertion_by = ['code']

    class Meta:
        verbose_name_plural = 'Areas'
        permissions = [
            ('can_manage_areas', 'Can manage areas'),
        ]

class Equipment(models.Model):
    """Equipment or machinery"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipment_set')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    manufacturer = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    installation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_expiration = models.DateField(null=True, blank=True)
    expected_lifetime = models.PositiveIntegerField(help_text="Expected lifetime in months", null=True, blank=True)
    is_critical = models.BooleanField(default=False, help_text="Indicates if this is critical equipment")
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_interval = models.PositiveIntegerField(help_text="Maintenance interval in days", null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_equipment')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_equipment')
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_absolute_url(self):
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

class TechnicalSpecification(models.Model):
    """Equipment technical specifications"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='technical_specifications')
    specification = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_specifications')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_specifications')

    def __str__(self):
        return f"{self.specification}: {self.value} {self.unit}"

    class Meta:
        ordering = ['specification']
        permissions = [
            ('can_manage_specifications', 'Can manage technical specifications'),
        ] 