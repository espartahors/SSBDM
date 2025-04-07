from django.db import models
from core.models import BaseModel


class TechnicalSpecification(BaseModel):
    """
    Equipment technical specifications with improved structure.
    """
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE, related_name='technical_specifications')
    specification = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.specification}: {self.value} {self.unit}"

    class Meta:
        ordering = ['specification']
        permissions = [
            ('can_manage_specifications', 'Can manage technical specifications'),
        ] 