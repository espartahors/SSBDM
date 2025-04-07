from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .models import AuditLog, SecuritySettings
import json

class AuditLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Skip logging for certain paths
        if request.path.startswith(('/admin/', '/static/', '/media/')):
            return response

        # Get user info
        user = request.user if request.user.is_authenticated else None
        user_id = user.id if user else None

        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Log the request
        if request.method in ['POST', 'PUT', 'DELETE']:
            try:
                action = {
                    'POST': 'create',
                    'PUT': 'update',
                    'DELETE': 'delete'
                }.get(request.method)

                # Get model name from URL
                model = request.path.split('/')[1].capitalize()

                # Get object ID if available
                object_id = request.resolver_match.kwargs.get('pk')

                # Create audit log entry
                AuditLog.objects.create(
                    user_id=user_id,
                    action=action,
                    model=model,
                    object_id=object_id,
                    details={
                        'path': request.path,
                        'method': request.method,
                        'data': request.POST.dict() if request.method == 'POST' else {}
                    },
                    ip_address=ip
                )
            except Exception as e:
                # Log the error but don't break the request
                pass

        return response

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get security settings
        settings = SecuritySettings.objects.first()
        if not settings:
            settings = SecuritySettings.objects.create()

        # Check session timeout
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if (timezone.now() - last_activity).total_seconds() > settings.session_timeout_minutes * 60:
                    # Session expired
                    request.session.flush()
                    return redirect('login')

            # Update last activity
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip permission check for certain paths
        if request.path.startswith(('/admin/', '/static/', '/media/', '/login/', '/logout/')):
            return None

        # Check if view requires permissions
        if hasattr(view_func, 'permission_required'):
            permissions = view_func.permission_required
            if isinstance(permissions, str):
                permissions = [permissions]

            # Check if user has required permissions
            if not request.user.has_perms(permissions):
                raise PermissionDenied

        return None 