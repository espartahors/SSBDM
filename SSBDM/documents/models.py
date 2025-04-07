from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import os
from django.utils import timezone
# Temporarily comment out Equipment import for testing
# from equipment_new.models import Equipment
import uuid

DOCUMENT_TYPE_CHOICES = (
    ('manual', 'Operating Manual'),
    ('datasheet', 'Technical Datasheet'),
    ('drawing', 'Technical Drawing'),
    ('schematic', 'Schematic'),
    ('certificate', 'Certificate'),
    ('procedure', 'Procedure'),
    ('warranty', 'Warranty'),
    ('inspection', 'Inspection Report'),
    ('maintenance', 'Maintenance Record'),
    ('other', 'Other'),
)

def document_file_path(instance, filename):
    """Generate file path for new document"""
    ext = filename.split('.')[-1]
    if instance.equipment:
        filename = f"{instance.equipment.code}-{instance.document_type}-{instance.id}.{ext}"
        return os.path.join('equipment_docs', instance.equipment.code, filename)
    else:
        filename = f"doc-{instance.document_type}-{instance.id}.{ext}"
        return os.path.join('general_docs', filename)

class DocumentCategory(models.Model):
    """Document classification category"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_document_categories')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_document_categories')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Document Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

class EquipmentDocument(models.Model):
    """Document related to equipment"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Temporarily change this to CharField for testing
    # equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='documents')
    equipment_code = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    file = models.FileField(upload_to=document_file_path)
    thumbnail = models.ImageField(upload_to='document_thumbnails/', null=True, blank=True)
    description = models.TextField(blank=True)
    document_number = models.CharField(max_length=50, blank=True, help_text="Document identifier or reference number")
    revision = models.CharField(max_length=10, blank=True, help_text="Document revision/version")
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    # Metadata
    upload_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_documents')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['document_type']),
            models.Index(fields=['upload_date']),
            models.Index(fields=['document_number']),
        ]
        permissions = [
            ('can_manage_documents', 'Can manage equipment documents'),
        ]

    def get_absolute_url(self):
        return reverse('documents:document_detail', kwargs={'pk': self.pk})
    
    def filename(self):
        return os.path.basename(self.file.name)
        
    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()
        
    @property
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower() 