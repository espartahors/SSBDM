from django.contrib.auth.models import User
from .models import Area, Equipment, MaintenanceLog, SparePart

def sidebar_context(request):
    """
    Add common data for the sidebar to all templates
    """
    areas = Area.objects.all()
    
    # Get counts for dashboard
    equipment_count = Equipment.objects.count()
    maintenance_count = MaintenanceLog.objects.count()
    spare_parts_count = SparePart.objects.count()
    user_count = User.objects.count()
    
    # Get low stock spare parts count
    low_stock_count = SparePart.objects.filter(
        quantity_in_stock__lt=models.F('minimum_stock')
    ).count()
    
    return {
        'sidebar_areas': areas,
        'stats': {
            'equipment_count': equipment_count,
            'maintenance_count': maintenance_count,
            'spare_parts_count': spare_parts_count,
            'user_count': user_count,
            'low_stock_count': low_stock_count
        }
    }