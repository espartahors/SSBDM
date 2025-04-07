from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    name = 'maintenance_new'
    verbose_name = 'Maintenance Management'
    
    def ready(self):
        """Import signals when the app is ready."""
        import maintenance_new.signals 