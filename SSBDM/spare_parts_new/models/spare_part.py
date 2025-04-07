from django.db import models
from django.urls import reverse
from django.utils import timezone
from core.models import BaseModel, CodeNameMixin, NotesMixin
from core.utils.constants import INVENTORY_STATUS_CHOICES, UNIT_CHOICES, CURRENCY_CHOICES
from .category import Category
from equipment_new.models import Equipment


class SparePart(BaseModel, CodeNameMixin, NotesMixin):
    """
    Spare part inventory model with improved structure.
    """
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    location = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    supplier = models.CharField(max_length=100, blank=True)
    supplier_reference = models.CharField(max_length=100, blank=True)
    lead_time = models.PositiveIntegerField(null=True, blank=True, help_text="Lead time in days")
    image = models.ImageField(upload_to='spare_parts/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='spare_parts')
    
    class Meta:
        verbose_name_plural = 'Spare Parts'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['name']),
            models.Index(fields=['current_stock']),
            models.Index(fields=['manufacturer']),
            models.Index(fields=['supplier']),
        ]
        permissions = [
            ('can_manage_spare_parts', 'Can manage spare parts'),
        ]
    
    def get_absolute_url(self):
        """Get URL for spare part detail view."""
        return reverse('spare_parts:spare_part_detail', kwargs={'pk': self.pk})
    
    @property
    def stock_status(self):
        """Calculate current stock status."""
        if self.current_stock <= 0:
            return 'out_of_stock'
        elif self.current_stock < self.minimum_stock:
            return 'low_stock'
        else:
            return 'in_stock'
            
    @property
    def stock_value(self):
        """Calculate total value of current stock."""
        if self.price:
            return self.price * self.current_stock
        return None 