from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User
import os

# Status Choices
STATUS_CHOICES = (
    ('operational', 'Operational'),
    ('maintenance', 'Under Maintenance'),
    ('breakdown', 'Breakdown'),
    ('inactive', 'Inactive'),
)

# Maintenance Type Choices
MAINTENANCE_TYPE_CHOICES = (
    ('preventive', 'Preventive'),
    ('corrective', 'Corrective'),
    ('predictive', 'Predictive'),
    ('emergency', 'Emergency'),
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
    equipment_type = models.CharField(max_length=100, help_text="Type of equipment")
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    installation_date = models.DateField(blank=True, null=True)
    last_maintenance_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='operational')
    description = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='equipment')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='components')
    
    def __str__(self):
        return f"{self.code}: {self.name}"
    
    def get_absolute_url(self):
        return reverse('maintenance:equipment_detail', kwargs={'pk': self.pk})


class TechnicalSpecification(models.Model):
    """
    Stores technical specifications for equipment
    """
    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE, related_name='technical_specs')
    specs_json = models.JSONField(help_text="Technical specifications as JSON")
    
    def __str__(self):
        return f"Specs for {self.equipment.code}"


class MaintenanceLog(models.Model):
    """
    Tracks maintenance activities on equipment
    """
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='maintenance_logs')
    title = models.CharField(max_length=200)
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    findings = models.TextField(blank=True, null=True)
    date = models.DateField()
    duration = models.DecimalField(max_digits=5, decimal_places=2, help_text="Duration in hours")
    technicians = models.ManyToManyField(User, related_name='maintenance_activities')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.maintenance_type} - {self.equipment.code} - {self.date}"
    
    def get_absolute_url(self):
        return reverse('maintenance:maintenance_detail', kwargs={'pk': self.pk})


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
    equipment = models.ManyToManyField(Equipment, related_name='spare_parts')
    
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
    DOCUMENT_TYPES = (
        ('manual', 'Operating Manual'),
        ('drawing', 'Technical Drawing'),
        ('certificate', 'Certificate'),
        ('procedure', 'Procedure'),
        ('other', 'Other'),
    )
    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=document_file_path)
    upload_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.equipment.code} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('maintenance:document_detail', kwargs={'pk': self.pk})
    
    def filename(self):
        return os.path.basename(self.file.name)