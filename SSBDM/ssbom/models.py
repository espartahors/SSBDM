from django.db import models
from django.core.exceptions import ValidationError
from equipment_new.models import Equipment, Area
from spare_parts_new.models import SparePart, Category
from documents.models import EquipmentDocument
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class BOMRelationship(models.Model):
    """
    A model to explicitly track relationships between equipment, spare parts, and documents
    for the Steel Bill of Materials (SSBOM) feature.
    """
    RELATIONSHIP_TYPES = (
        ('component', 'Component'),
        ('assembly', 'Assembly'),
        ('replacement', 'Replacement Part'),
        ('consumable', 'Consumable'),
        ('tool', 'Tool'),
        ('documentation', 'Documentation'),
        ('assembly_of', 'Assembly Of'),  # Inverse relationship
        ('component_of', 'Component Of'), # Inverse relationship
        ('alternative', 'Alternative Part'),
    )
    
    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The parent equipment
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='bom_relationships')
    
    # Related item - can be a spare part, document, or even another equipment
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, null=True, blank=True, related_name='equipment_relationships')
    document = models.ForeignKey(EquipmentDocument, on_delete=models.CASCADE, null=True, blank=True, related_name='equipment_relationships')
    related_equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True, related_name='parent_relationships')
    
    # Relationship type and additional information
    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES, default='component')
    quantity = models.PositiveIntegerField(default=1)
    position = models.CharField(max_length=100, blank=True, help_text="Physical position or location of the item")
    criticality = models.PositiveSmallIntegerField(default=3, choices=[(1, 'Critical'), (2, 'Important'), (3, 'Normal'), (4, 'Optional')])
    notes = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_relationships')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_relationships')
    
    class Meta:
        verbose_name = "BOM Relationship"
        verbose_name_plural = "BOM Relationships"
        ordering = ['equipment__name', 'relationship_type', 'criticality']
        indexes = [
            models.Index(fields=['relationship_type']),
            models.Index(fields=['criticality']),
            models.Index(fields=['created_at']),
        ]
        # Ensure we don't have duplicate relationships of the same type
        constraints = [
            models.UniqueConstraint(
                fields=['equipment', 'spare_part', 'relationship_type'], 
                condition=models.Q(spare_part__isnull=False),
                name='unique_equipment_sparepart_relation'
            ),
            models.UniqueConstraint(
                fields=['equipment', 'document', 'relationship_type'], 
                condition=models.Q(document__isnull=False),
                name='unique_equipment_document_relation'
            ),
            models.UniqueConstraint(
                fields=['equipment', 'related_equipment', 'relationship_type'], 
                condition=models.Q(related_equipment__isnull=False),
                name='unique_equipment_equipment_relation'
            ),
        ]
    
    def __str__(self):
        if self.spare_part:
            return f"{self.equipment.name} - {self.spare_part.name} ({self.get_relationship_type_display()})"
        elif self.document:
            return f"{self.equipment.name} - {self.document.title} ({self.get_relationship_type_display()})"
        elif self.related_equipment:
            return f"{self.equipment.name} - {self.related_equipment.name} ({self.get_relationship_type_display()})"
        return f"{self.equipment.name} - Unknown ({self.get_relationship_type_display()})"
    
    def clean(self):
        """Ensure at least one related item is specified and validate relationship logic"""
        if not self.spare_part and not self.document and not self.related_equipment:
            raise ValidationError("Either a spare part, document, or related equipment must be specified")
        
        # Count how many foreign keys are set
        related_count = sum(1 for item in [self.spare_part, self.document, self.related_equipment] if item is not None)
        
        if related_count > 1:
            raise ValidationError("Only one of spare part, document, or related equipment can be specified")
            
        # Validate no circular relationships
        if self.related_equipment and self.related_equipment == self.equipment:
            raise ValidationError("An equipment cannot have a relationship with itself")
            
        # Validate relationship type is appropriate for the related item
        doc_types = ['documentation']
        equipment_types = ['component', 'assembly', 'assembly_of', 'component_of']
        
        if self.document and self.relationship_type not in doc_types:
            raise ValidationError(f"Documents can only have relationship types: {', '.join(doc_types)}")
            
        if self.related_equipment and self.relationship_type not in equipment_types:
            raise ValidationError(f"Equipment-to-equipment relationships can only have types: {', '.join(equipment_types)}")
            
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EquipmentSparePartUsage(models.Model):
    """
    Tracks actual usage of spare parts on equipment, including installation history
    and current status. This is different from BOMRelationship which defines the 
    theoretical relationships.
    """
    STATUS_CHOICES = (
        ('installed', 'Currently Installed'),
        ('removed', 'Removed'),
        ('replaced', 'Replaced'),
        ('pending', 'Pending Installation'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='spare_part_usages')
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='equipment_usages')
    
    # Can optionally link to a relationship if it exists
    relationship = models.ForeignKey(BOMRelationship, on_delete=models.SET_NULL, null=True, blank=True, 
                                     related_name='usages', help_text="Associated BOM relationship if applicable")
    
    # Usage details
    installation_date = models.DateTimeField(null=True, blank=True)
    removal_date = models.DateTimeField(null=True, blank=True)
    position = models.CharField(max_length=100, blank=True, help_text="Physical position or location of the spare part")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='installed')
    serial_number = models.CharField(max_length=100, blank=True, help_text="Serial number of this specific part instance")
    lot_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Historical links
    replaced_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='replaced_parts', help_text="Newer part that replaced this one")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='created_part_usages')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='updated_part_usages')
    
    class Meta:
        verbose_name = "Equipment Spare Part Usage"
        verbose_name_plural = "Equipment Spare Part Usages"
        ordering = ['-installation_date', 'status']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['installation_date']),
            models.Index(fields=['serial_number']),
        ]
    
    def __str__(self):
        return f"{self.spare_part.name} on {self.equipment.name} ({self.get_status_display()})"
    
    def clean(self):
        """Validate usage logic"""
        # If status is 'installed', ensure installation_date is set
        if self.status == 'installed' and not self.installation_date:
            self.installation_date = timezone.now()
            
        # If status is 'removed' or 'replaced', ensure removal_date is set
        if self.status in ['removed', 'replaced'] and not self.removal_date:
            self.removal_date = timezone.now()
            
        # If this usage is replaced, ensure the status is set to 'replaced'
        if self.replaced_by and self.status != 'replaced':
            self.status = 'replaced'
            
        # Ensure removal date is after installation date
        if self.installation_date and self.removal_date and self.removal_date < self.installation_date:
            raise ValidationError("Removal date cannot be before installation date")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BOMChangeLog(models.Model):
    """Track changes to BOM relationships for audit purposes"""
    ACTION_TYPES = (
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    relationship = models.UUIDField(help_text="UUID of the affected BOM relationship")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='bom_change_logs')
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    description = models.TextField(help_text="Description of the change")
    previous_state = models.JSONField(null=True, blank=True, help_text="JSON representation of previous state")
    new_state = models.JSONField(null=True, blank=True, help_text="JSON representation of new state")
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bom_changes')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['relationship']),
        ]
        
    def __str__(self):
        return f"{self.get_action_display()} relationship for {self.equipment.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class EquipmentHierarchy(models.Model):
    """
    Materialized view of equipment hierarchies to improve query performance.
    This is updated whenever BOMRelationships change.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ancestor = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='descendant_paths')
    descendant = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='ancestor_paths')
    path_length = models.PositiveIntegerField(help_text="Number of relationships between ancestor and descendant")
    relationship_path = models.JSONField(help_text="JSON array describing the path of relationships")
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [('ancestor', 'descendant')]
        indexes = [
            models.Index(fields=['ancestor']),
            models.Index(fields=['descendant']),
            models.Index(fields=['path_length']),
        ]
        
    def __str__(self):
        return f"{self.ancestor.name} → {self.descendant.name} (depth: {self.path_length})" 