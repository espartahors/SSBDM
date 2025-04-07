"""
Base service layer for business logic.
This implements the repository pattern to separate data access from business logic.
"""
from django.db.models import Model, QuerySet
from typing import TypeVar, Generic, List, Optional, Dict, Any, Union

T = TypeVar('T', bound=Model)


class BaseService(Generic[T]):
    """
    Base service class for all services.
    
    This class implements common CRUD operations and can be extended
    for specific business logic.
    """
    model_class = None
    
    def __init__(self, user=None):
        """
        Initialize service with optional user for tracking changes.
        
        Args:
            user: The user performing the operations
        """
        if self.model_class is None:
            raise ValueError("model_class must be defined in child class")
        self.user = user
    
    def get_queryset(self) -> QuerySet:
        """
        Return the base queryset for the model.
        
        Returns:
            QuerySet: Base queryset
        """
        return self.model_class.objects.all()
    
    def get_by_id(self, pk) -> Optional[T]:
        """
        Get an object by its primary key.
        
        Args:
            pk: Primary key
            
        Returns:
            Object instance or None
        """
        try:
            return self.get_queryset().get(pk=pk)
        except self.model_class.DoesNotExist:
            return None
    
    def list(self, **filters) -> QuerySet:
        """
        List objects with optional filters.
        
        Args:
            **filters: Filter parameters
            
        Returns:
            QuerySet of objects
        """
        return self.get_queryset().filter(**filters)
    
    def create(self, **data) -> T:
        """
        Create a new object.
        
        Args:
            **data: Object data
            
        Returns:
            Created object
        """
        if self.user and 'created_by' not in data:
            data['created_by'] = self.user
        
        return self.model_class.objects.create(**data)
    
    def update(self, instance: T, **data) -> T:
        """
        Update an existing object.
        
        Args:
            instance: Object to update
            **data: Updated data
            
        Returns:
            Updated object
        """
        if self.user and hasattr(instance, 'updated_by'):
            instance.updated_by = self.user
        
        for key, value in data.items():
            setattr(instance, key, value)
        
        instance.save()
        return instance
    
    def delete(self, instance: T) -> bool:
        """
        Delete an object.
        
        Args:
            instance: Object to delete
            
        Returns:
            True if successful
        """
        instance.delete()
        return True
        
    def bulk_create(self, objects_data: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple objects.
        
        Args:
            objects_data: List of object data
            
        Returns:
            List of created objects
        """
        objects = []
        for data in objects_data:
            if self.user and 'created_by' not in data:
                data['created_by'] = self.user
            objects.append(self.model_class(**data))
        
        return self.model_class.objects.bulk_create(objects) 