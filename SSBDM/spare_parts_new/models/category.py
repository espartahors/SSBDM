from django.db import models
from django.urls import reverse
from core.models import BaseTreeModel


class Category(BaseTreeModel):
    """
    Spare part category model with hierarchical structure.
    """
    
    class Meta(BaseTreeModel.Meta):
        verbose_name_plural = "Categories"
        permissions = [
            ('can_manage_categories', 'Can manage spare part categories'),
        ]
    
    def get_absolute_url(self):
        """Get URL for category detail view."""
        return reverse('spare_parts:category_detail', kwargs={'pk': self.pk}) 