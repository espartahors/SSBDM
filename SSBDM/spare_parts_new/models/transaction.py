from django.db import models
from django.utils import timezone
from core.models import BaseModel
from core.utils.constants import TRANSACTION_TYPES
from .spare_part import SparePart
from equipment_new.models import Equipment


class SparePartTransaction(BaseModel):
    """
    Spare part transaction model for tracking inventory movements.
    """
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, 
                                 help_text="Equipment this part was used for")
    date = models.DateTimeField(default=timezone.now)
    reference = models.CharField(max_length=100, blank=True, help_text="Reference number, work order, etc.")
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['date']),
        ]
        permissions = [
            ('can_record_transactions', 'Can record spare part transactions'),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.spare_part.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        # Update the stock quantity based on transaction type
        if not self.pk:  # Only for new transactions
            if self.transaction_type == 'received' or self.transaction_type == 'returned':
                self.spare_part.current_stock += self.quantity
            elif self.transaction_type == 'issued':
                self.spare_part.current_stock -= min(self.quantity, self.spare_part.current_stock)
            elif self.transaction_type == 'adjusted':
                # For adjustments, the quantity field represents the change (positive or negative)
                self.spare_part.current_stock = max(0, self.spare_part.current_stock + self.quantity)
                
            self.spare_part.save()
            
        super().save(*args, **kwargs) 