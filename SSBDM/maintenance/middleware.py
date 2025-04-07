from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from .models import AuditLog, Area, MaintenanceLog, SparePart
from equipment.models import Equipment
from .permissions import has_permission, can_modify_equipment

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.model_map = {
            'equipment': Equipment,
            'maintenancelog': MaintenanceLog,
            'sparepart': SparePart,
            'area': Area
        }

    def __call__(self, request):
        # Process request
        self._check_permissions(request)
        response = self.get_response(request)
        # Log actions
        self._log_actions(request)
        return response

    def _check_permissions(self, request):
        """Check user permissions for the request"""
        if request.method in ['POST', 'PUT', 'DELETE'] and request.user.is_authenticated:
            path_parts = request.path.split('/')
            if len(path_parts) >= 3:
                model_name = path_parts[2]
                action = 'add' if request.method == 'POST' else 'change' if request.method == 'PUT' else 'delete'
                
                if model_name in self.model_map:
                    if model_name == 'equipment':
                        equipment_type = request.POST.get('equipment_type', 'general')
                        if not can_modify_equipment(request.user, equipment_type):
                            raise PermissionDenied(f"You don't have permission to modify {equipment_type} equipment")
                    elif not has_permission(request.user, self.model_map[model_name], action):
                        raise PermissionDenied("You don't have permission to perform this action")

    def _log_actions(self, request):
        """Log user actions"""
        if request.user.is_authenticated and request.method in ['POST', 'DELETE']:
            path_parts = request.path.split('/')
            if len(path_parts) >= 3:
                model_name = path_parts[2]
                
                if request.method == 'POST':
                    equipment_type = request.POST.get('equipment_type', 'general')
                    details = f"User {request.user.username} performed {request.method} on {model_name} (Type: {equipment_type})"
                    action = 'create' if 'add' in request.path else 'update'
                else:  # DELETE
                    object_id = path_parts[3] if len(path_parts) >= 4 else None
                    details = f"User {request.user.username} deleted {model_name} with ID {object_id}"
                    action = 'delete'
                
                AuditLog.objects.create(
                    user=request.user,
                    action=action,
                    model_name=model_name,
                    object_id=object_id if request.method == 'DELETE' else None,
                    details=details,
                    timestamp=timezone.now()
                ) 