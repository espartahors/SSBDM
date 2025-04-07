from django.db import models
from django.urls import reverse
from core.models import BaseTreeModel


class Area(BaseTreeModel):
    """
    Plant area or section represented as a hierarchical tree structure.
    """
    
    class Meta(BaseTreeModel.Meta):
        verbose_name_plural = 'Areas'
        permissions = [
            ('can_manage_areas', 'Can manage areas'),
        ]
    
    def get_absolute_url(self):
        """Get URL for area detail view."""
        return reverse('equipment:area_detail', kwargs={'pk': self.pk}) 