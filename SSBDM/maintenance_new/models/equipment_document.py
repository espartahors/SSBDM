import os
from django.db import models
from django.urls import reverse
from core.models import BaseModel
from core.utils.constants import DOCUMENT_TYPE_CHOICES
from equipment_new.models import Equipment


def document_file_path(instance, filename):
    """Generate file path for new document"""
    ext = filename.split('.')[-1]
    filename = f"{instance.equipment.code}-{instance.document_type}-{instance.id}.{ext}"
    return os.path.join('equipment_docs', instance.equipment.code, filename)


class EquipmentDocument(BaseModel):
    """
    Model for equipment documents with improved structure.
    Stores documents related to equipment (manuals, drawings, etc.)
    """
    equipment = models.ForeignKey(
        Equipment, 
        on_delete=models.CASCADE, 
        related_name='maintenance_documents'
    )
    title = models.CharField(max_length=200)
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPE_CHOICES
    )
    file = models.FileField(upload_to=document_file_path)
    upload_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['title']
        permissions = [
            ('can_manage_documents', 'Can manage equipment documents'),
        ]
    
    def __str__(self):
        return f"{self.equipment.code} - {self.title}"
    
    def get_absolute_url(self):
        return reverse('maintenance:document_detail', kwargs={'pk': self.pk})
    
    def filename(self):
        """Get the actual filename."""
        return os.path.basename(self.file.name) 