from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff users to edit.
    Non-staff users can view, but not modify.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to staff
        return request.user.is_authenticated and request.user.is_staff


class MaintenancePermission(permissions.BasePermission):
    """
    Custom permission for maintenance-related objects.
    
    - Admin users can do anything
    - Staff users can create, view, and update
    - Maintenance users can create, view, and update
    - Other authenticated users can only view
    - Unauthenticated users have no access
    """
    
    def has_permission(self, request, view):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
        
        # Admin users can do anything
        if request.user.is_superuser:
            return True
        
        # Staff and maintenance users can create and view
        if request.user.is_staff or request.user.has_perm('maintenance_new.can_manage_maintenance'):
            return True
        
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.is_superuser:
            return True
        
        # Staff and maintenance users can update and view
        if request.user.is_staff or request.user.has_perm('maintenance_new.can_manage_maintenance'):
            return True
        
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS


class TaskPermission(permissions.BasePermission):
    """
    Custom permission for maintenance tasks.
    
    - Admin users can do anything
    - Staff users can create, view, and update
    - Maintenance users can create, view, and update
    - Task assignees can update their own tasks
    - Other authenticated users can only view
    - Unauthenticated users have no access
    """
    
    def has_permission(self, request, view):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
        
        # Admin users can do anything
        if request.user.is_superuser:
            return True
        
        # Staff and maintenance users can create and view
        if request.user.is_staff or request.user.has_perm('maintenance_new.can_manage_tasks'):
            return True
        
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.is_superuser:
            return True
        
        # Staff and maintenance users can update and view
        if request.user.is_staff or request.user.has_perm('maintenance_new.can_manage_tasks'):
            return True
        
        # Task assignees can update their own tasks
        if obj.assigned_to == request.user:
            return True
        
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS


class DocumentPermission(permissions.BasePermission):
    """
    Custom permission for equipment documents.
    
    - Admin users can do anything
    - Staff users can create, view, and update
    - Maintenance users can create, view, and update
    - Other authenticated users can only view
    - Unauthenticated users have no access
    """
    
    def has_permission(self, request, view):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
        
        # Admin users can do anything
        if request.user.is_superuser:
            return True
        
        # Staff and maintenance users can create and view
        if request.user.is_staff or request.user.has_perm('maintenance_new.can_manage_documents'):
            return True
        
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.is_superuser:
            return True
        
        # Staff and maintenance users can update and view
        if request.user.is_staff or request.user.has_perm('maintenance_new.can_manage_documents'):
            return True
        
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS


class AuditLogPermission(permissions.BasePermission):
    """
    Custom permission for audit logs.
    
    - Admin users can view
    - Staff users can view
    - Other users have no access
    - No users can modify (read-only)
    """
    
    def has_permission(self, request, view):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
        
        # Only safe methods allowed (GET, HEAD, OPTIONS)
        if not request.method in permissions.SAFE_METHODS:
            return False
        
        # Only admin and staff can view
        return request.user.is_superuser or request.user.is_staff or request.user.has_perm('maintenance_new.can_view_audit_logs') 