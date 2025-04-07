from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
import os
from django.utils import timezone
from equipment.models import Equipment as EquipmentModel

# Choices
STATUS_CHOICES = (
    ('operational', 'Operational'),
    ('maintenance', 'Under Maintenance'),
    ('breakdown', 'Breakdown'),
    ('inactive', 'Inactive'),
)

MAINTENANCE_TYPE_CHOICES = (
    ('preventive', 'Preventive'),
    ('corrective', 'Corrective'),
    ('predictive', 'Predictive'),
    ('emergency', 'Emergency'),
)

EQUIPMENT_TYPE_CHOICES = (
    ('electric', 'Electrical'),
    ('mechanical', 'Mechanical'),
    ('general', 'General'),
)

DOCUMENT_TYPE_CHOICES = (
    ('manual', 'Operating Manual'),
    ('drawing', 'Technical Drawing'),
    ('certificate', 'Certificate'),
    ('procedure', 'Procedure'),
    ('other', 'Other'),
)

def get_absolute_url(self):
    return reverse('maintenance:maintenance_log_detail', kwargs={'pk': self.pk})

class Area(MPTTModel):
    """
    Represents a plant area or section in the hierarchical structure.
    """
    code = models.CharField(max_length=10, unique=True, help_text="Area code (e.g., ASU, FTP)")
    name = models.CharField(max_length=100, help_text="Area name")
    description = models.TextField(blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class MPTTMeta:
        order_insertion_by = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('maintenance:area_detail', kwargs={'pk': self.pk})


class Equipment(models.Model):
    """
    Represents a piece of equipment like Hydraulic System, Compressor, etc.
    """
    code = models.CharField(max_length=20, unique=True, help_text="Equipment code (e.g., SMP-EAF-HYD-0001)")
    name = models.CharField(max_length=100, help_text="Equipment name")
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES, default='general')
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    installation_date = models.DateField(blank=True, null=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    description = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='equipment')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='components')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('maintenance:equipment_detail', kwargs={'pk': self.pk})


class TechnicalSpecification(models.Model):
    """
    Stores technical specifications for equipment
    """
    equipment = models.OneToOneField(EquipmentModel, on_delete=models.CASCADE, related_name='technical_specs')
    specs_json = models.JSONField(help_text="Technical specifications as JSON")
    
    def __str__(self):
        return f"Specs for {self.equipment.code}"


class MaintenanceLog(models.Model):
    MAINTENANCE_TYPES = (
        ('preventive', 'Preventive Maintenance'),
        ('corrective', 'Corrective Maintenance'),
        ('predictive', 'Predictive Maintenance'),
        ('inspection', 'Inspection'),
        ('calibration', 'Calibration'),
        ('other', 'Other'),
    )
    
    MAINTENANCE_RESULTS = (
        ('successful', 'Successful'),
        ('partial', 'Partially Completed'),
        ('failed', 'Failed'),
        ('postponed', 'Postponed'),
    )

    equipment = models.ForeignKey(EquipmentModel, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    duration = models.DecimalField(max_digits=10, decimal_places=2, help_text='Duration in hours')
    technicians = models.ManyToManyField(User, related_name='maintenance_work')
    observations = models.TextField(blank=True)
    maintenance_result = models.CharField(max_length=20, choices=MAINTENANCE_RESULTS, blank=True, null=True)
    result_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_maintenance_logs')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_maintenance_logs', blank=True)

    def __str__(self):
        return f"{self.equipment.code} - {self.title} ({self.date})"
        
    def get_absolute_url(self):
        return reverse('maintenance:log_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-date']
        permissions = [
            ('can_manage_maintenance', 'Can manage maintenance logs'),
        ]


class MaintenanceTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    maintenance_log = models.ForeignKey(MaintenanceLog, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    due_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task for {self.maintenance_log.equipment.code} - {self.description[:50]}"

    class Meta:
        ordering = ['-due_date']
        permissions = [
            ('can_manage_tasks', 'Can manage maintenance tasks'),
        ]


class SparePart(models.Model):
    """
    Represents spare parts used in equipment
    """
    part_number = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    equipment = models.ManyToManyField(EquipmentModel, related_name='spare_parts')
    
    def __str__(self):
        return f"{self.part_number}: {self.description} ({self.quantity_in_stock} in stock)"
    
    def get_absolute_url(self):
        return reverse('maintenance:spare_part_detail', kwargs={'pk': self.pk})

    def stock_status(self):
        if self.quantity_in_stock == 0:
            return "out_of_stock"
        elif self.quantity_in_stock < self.minimum_stock:
            return "low_stock"
        else:
            return "in_stock"


def document_file_path(instance, filename):
    """Generate file path for new document"""
    ext = filename.split('.')[-1]
    filename = f"{instance.equipment.code}-{instance.document_type}-{instance.id}.{ext}"
    return os.path.join('equipment_docs', instance.equipment.code, filename)


class EquipmentDocument(models.Model):
    """
    Stores documents related to equipment (manuals, drawings, etc.)
    """
    equipment = models.ForeignKey(EquipmentModel, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to=document_file_path)
    upload_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.equipment.code} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('maintenance:document_detail', kwargs={'pk': self.pk})
    
    def filename(self):
        return os.path.basename(self.file.name)


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.model_name} - {self.timestamp}"