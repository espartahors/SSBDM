from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from .base import BaseModel
from .mixins import CodeNameMixin


class BaseTreeModel(MPTTModel, CodeNameMixin, BaseModel):
    """
    Base model for tree structures like categories, areas, etc.
    Uses MPTT for efficient tree operations.
    """
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    
    class Meta:
        abstract = True
        
    class MPTTMeta:
        order_insertion_by = ['code'] 