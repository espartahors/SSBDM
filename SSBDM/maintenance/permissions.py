from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Equipment, MaintenanceLog, SparePart, Area

# Role definitions
ROLES = {
    'admin': 'System Administrators',
    'maintenance_manager': 'Maintenance Managers',
    'electrician': 'Electricians',
    'mechanic': 'Mechanics',
    'technician': 'Technicians',
    'operator': 'Equipment Operators',
}

# Model permissions
MODEL_PERMISSIONS = {
    'equipment': {
        'admin': ['view', 'add', 'change', 'delete'],
        'maintenance_manager': ['view', 'add', 'change', 'delete'],
        'electrician': ['view', 'change'],
        'mechanic': ['view', 'change'],
        'technician': ['view'],
        'operator': ['view'],
    },
    'maintenancelog': {
        'admin': ['view', 'add', 'change', 'delete'],
        'maintenance_manager': ['view', 'add', 'change', 'delete'],
        'electrician': ['view', 'add', 'change'],
        'mechanic': ['view', 'add', 'change'],
        'technician': ['view', 'add'],
        'operator': ['view'],
    },
    'sparepart': {
        'admin': ['view', 'add', 'change', 'delete'],
        'maintenance_manager': ['view', 'add', 'change', 'delete'],
        'electrician': ['view'],
        'mechanic': ['view'],
        'technician': ['view'],
        'operator': ['view'],
    },
    'area': {
        'admin': ['view', 'add', 'change', 'delete'],
        'maintenance_manager': ['view', 'add', 'change', 'delete'],
        'electrician': ['view'],
        'mechanic': ['view'],
        'technician': ['view'],
        'operator': ['view'],
    }
}

# Equipment type permissions
EQUIPMENT_PERMISSIONS = {
    'electric': {
        'electrician': True,
        'maintenance_manager': True,
        'admin': True
    },
    'mechanical': {
        'mechanic': True,
        'maintenance_manager': True,
        'admin': True
    },
    'general': {
        'technician': True,
        'maintenance_manager': True,
        'admin': True
    }
}

def setup_permissions():
    """Initialize groups and permissions"""
    # Create groups
    for group_name, group_desc in ROLES.items():
        Group.objects.get_or_create(name=group_name)
    
    # Model mapping
    model_map = {
        'equipment': Equipment,
        'maintenancelog': MaintenanceLog,
        'sparepart': SparePart,
        'area': Area
    }
    
    # Assign permissions
    for model_name, role_permissions in MODEL_PERMISSIONS.items():
        if model_name in model_map:
            content_type = ContentType.objects.get_for_model(model_map[model_name])
            
            for role, permissions in role_permissions.items():
                group = Group.objects.get(name=role)
                for permission in permissions:
                    codename = f'{permission}_{model_name}'
                    try:
                        permission_obj = Permission.objects.get(
                            content_type=content_type,
                            codename=codename
                        )
                        group.permissions.add(permission_obj)
                    except Permission.DoesNotExist:
                        pass

def get_user_permissions(user):
    """Get all permissions for a user"""
    if user.is_superuser:
        return Permission.objects.all()
    return user.user_permissions.all() | Permission.objects.filter(group__user=user)

def has_permission(user, model, action):
    """Check if user has specific permission"""
    if user.is_superuser:
        return True
    content_type = ContentType.objects.get_for_model(model)
    return user.has_perm(f'{content_type.app_label}.{action}_{model.__name__.lower()}')

def get_user_role(user):
    """Get user's primary role"""
    if user.is_superuser:
        return 'admin'
    groups = user.groups.all()
    return groups.first().name if groups.exists() else None

def can_modify_equipment(user, equipment_type):
    """Check if user can modify specific equipment type"""
    if user.is_superuser:
        return True
    role = get_user_role(user)
    return EQUIPMENT_PERMISSIONS.get(equipment_type, {}).get(role, False) if role else False 