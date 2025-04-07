from django.db.models import Q
from django.utils import timezone
from core.services.base_service import BaseService
from ..models import TechnicalSpecification, Equipment


class TechnicalSpecificationService(BaseService):
    """
    Service for managing technical specifications.
    """
    model = TechnicalSpecification
    
    def get_queryset(self):
        """Get base queryset for technical specifications."""
        return TechnicalSpecification.objects.all()
    
    def create(self, equipment, specification, value, unit=None, **kwargs):
        """
        Create a new technical specification.
        
        Args:
            equipment: Equipment instance or ID.
            specification: Specification name.
            value: Specification value.
            unit: Measurement unit (optional).
            
        Returns:
            Created TechnicalSpecification instance.
        """
        if isinstance(equipment, str):
            equipment = Equipment.objects.get(id=equipment)
            
        spec = TechnicalSpecification(
            equipment=equipment,
            specification=specification,
            value=value,
            unit=unit or '',
            created_by=self.user,
            updated_by=self.user
        )
        spec.save()
        return spec
    
    def update(self, instance, **kwargs):
        """
        Update an existing technical specification.
        
        Args:
            instance: TechnicalSpecification instance to update.
            **kwargs: Fields to update.
            
        Returns:
            Updated TechnicalSpecification instance.
        """
        for field, value in kwargs.items():
            setattr(instance, field, value)
            
        instance.updated_by = self.user
        instance.save()
        return instance
    
    def search(self, query):
        """
        Search for technical specifications.
        
        Args:
            query: Search query string.
            
        Returns:
            Queryset of matching technical specifications.
        """
        return self.get_queryset().filter(
            Q(specification__icontains=query) |
            Q(value__icontains=query) |
            Q(unit__icontains=query) |
            Q(equipment__name__icontains=query) |
            Q(equipment__code__icontains=query)
        )
    
    def get_by_equipment(self, equipment_id):
        """
        Get all specifications for a specific equipment.
        
        Args:
            equipment_id: Equipment ID.
            
        Returns:
            Queryset of technical specifications for the equipment.
        """
        return self.get_queryset().filter(equipment_id=equipment_id)
    
    def get_by_spec_type(self, spec_type):
        """
        Get all specifications of a specific type.
        
        Args:
            spec_type: Specification type.
            
        Returns:
            Queryset of technical specifications of the specified type.
        """
        return self.get_queryset().filter(specification=spec_type) 