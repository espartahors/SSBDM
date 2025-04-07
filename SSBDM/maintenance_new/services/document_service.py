from django.db.models import Q, Count
from core.services.base_service import BaseService
from ..models import EquipmentDocument


class DocumentService(BaseService[EquipmentDocument]):
    """
    Service class for EquipmentDocument entity.
    Implements business logic for equipment document management.
    """
    model_class = EquipmentDocument
    
    def get_queryset(self):
        """Return the base queryset with related objects."""
        return super().get_queryset().select_related(
            'equipment',
            'created_by',
            'updated_by'
        )
    
    def search(self, query):
        """
        Search for documents based on various criteria.
        
        Args:
            query (str): Search query
            
        Returns:
            QuerySet: Filtered documents
        """
        return self.get_queryset().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(equipment__code__icontains=query) |
            Q(equipment__name__icontains=query)
        )
    
    def get_by_equipment(self, equipment_id):
        """
        Get documents for a specific equipment.
        
        Args:
            equipment_id: Equipment ID
            
        Returns:
            QuerySet: Documents for specified equipment
        """
        return self.get_queryset().filter(equipment_id=equipment_id)
    
    def get_by_type(self, document_type):
        """
        Get documents by type.
        
        Args:
            document_type (str): Document type
            
        Returns:
            QuerySet: Documents of specified type
        """
        return self.get_queryset().filter(document_type=document_type)
    
    def get_document_statistics(self):
        """
        Get statistics about documents.
        
        Returns:
            dict: Document statistics
        """
        total = self.get_queryset().count()
        
        # Documents by type
        type_counts = dict(
            self.get_queryset()
            .values('document_type')
            .annotate(count=Count('id'))
            .values_list('document_type', 'count')
        )
        
        # Equipment with most documents
        equipment_stats = list(
            self.get_queryset()
            .values('equipment__code', 'equipment__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        
        # Latest documents
        latest_docs = list(
            self.get_queryset()
            .order_by('-upload_date')
            .values('id', 'title', 'equipment__code', 'document_type', 'upload_date')[:5]
        )
        
        return {
            'total': total,
            'type_counts': type_counts,
            'equipment_stats': equipment_stats,
            'latest_docs': latest_docs,
        } 