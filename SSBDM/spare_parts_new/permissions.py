from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow staff users to edit objects.
    Read-only permission is allowed for any authenticated user.
    """
    
    def has_permission(self, request, view):
        # Allow GET, HEAD or OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True
            
        # Write permissions only for staff users
        return request.user.is_staff
        
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS and request.user.is_authenticated:
            return True
            
        # Write permissions only for staff users
        return request.user.is_staff


class SparePartPermission(permissions.BasePermission):
    """
    Custom permission for spare parts management:
    - Admin users have full access
    - Staff users can create, view, and update parts
    - Other authenticated users can only view
    - No access for unauthenticated users
    """
    
    def has_permission(self, request, view):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
            
        # Full access for admin users
        if request.user.is_superuser:
            return True
            
        # Staff can create and view
        if request.user.is_staff:
            return True
            
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS
        
    def has_object_permission(self, request, view, obj):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
            
        # Full access for admin users
        if request.user.is_superuser:
            return True
            
        # Staff can view and update
        if request.user.is_staff:
            return True
            
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS


class TransactionPermission(permissions.BasePermission):
    """
    Custom permission for inventory transactions:
    - Admin users have full access
    - Staff users can create, view, and update transactions
    - Warehouse users (custom group) can create and view transactions
    - Other authenticated users can only view
    - No access for unauthenticated users
    """
    
    def has_permission(self, request, view):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
            
        # Full access for admin users
        if request.user.is_superuser:
            return True
            
        # Staff can create and view
        if request.user.is_staff:
            return True
            
        # Warehouse users can create and view
        if request.user.groups.filter(name='Warehouse').exists():
            if request.method == 'DELETE':
                return False
            return True
            
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS
        
    def has_object_permission(self, request, view, obj):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
            
        # Full access for admin users
        if request.user.is_superuser:
            return True
            
        # Staff can view and update
        if request.user.is_staff:
            return True
            
        # Warehouse users can view and update their own transactions
        if request.user.groups.filter(name='Warehouse').exists():
            if request.method == 'DELETE':
                return False
            if hasattr(obj, 'created_by') and obj.created_by == request.user:
                return True
            return request.method in permissions.SAFE_METHODS
            
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS


class CategoryPermission(permissions.BasePermission):
    """
    Custom permission for spare part categories:
    - Admin users have full access
    - Staff users can create, view, and update categories
    - Other authenticated users can only view
    - No access for unauthenticated users
    """
    
    def has_permission(self, request, view):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
            
        # Full access for admin users
        if request.user.is_superuser:
            return True
            
        # Staff can create and view
        if request.user.is_staff:
            return True
            
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS
        
    def has_object_permission(self, request, view, obj):
        # No access for unauthenticated users
        if not request.user.is_authenticated:
            return False
            
        # Full access for admin users
        if request.user.is_superuser:
            return True
            
        # Staff can view and update
        if request.user.is_staff:
            return True
            
        # Other authenticated users can only view
        return request.method in permissions.SAFE_METHODS 