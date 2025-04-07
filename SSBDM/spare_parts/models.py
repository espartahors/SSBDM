from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from equipment_new.models import Equipment
from django.db.models import F, Q, Case, When, Value, IntegerField
from mptt.models import MPTTModel, TreeForeignKey
import uuid

class Category(MPTTModel):
    """Model for spare part categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_categories')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_categories')
    
    def __str__(self):
        return self.name

    class MPTTMeta:
        order_insertion_by = ['name']
        
    class Meta:
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

class SparePart(models.Model):
    """Model for spare parts inventory"""
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    current_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=20, default='pcs', help_text="Unit of measurement (pcs, kg, l, etc.)")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    location = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    supplier = models.CharField(max_length=100, blank=True)
    supplier_reference = models.CharField(max_length=100, blank=True)
    lead_time = models.PositiveIntegerField(null=True, blank=True, help_text="Lead time in days")
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='spare_parts/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='spare_parts')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_spare_parts')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_spare_parts')
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_absolute_url(self):
        return reverse('spare_parts:spare_part_detail', kwargs={'pk': self.pk})
    
    @property
    def stock_status(self):
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
    
    class Meta:
        ordering = ['name']
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

class SparePartTransaction(models.Model):
    """Model for spare part transactions (in/out)"""
    TRANSACTION_TYPES = [
        ('received', 'Received'),
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('adjusted', 'Inventory Adjustment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, 
                                 help_text="Equipment this part was used for")
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True, help_text="Reference number, work order, etc.")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_transactions')
    
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
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['transaction_type']),
            models.Index(fields=['date']),
        ]
        permissions = [
            ('can_record_transactions', 'Can record spare part transactions'),
        ] 