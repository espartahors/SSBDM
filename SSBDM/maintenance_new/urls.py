from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MaintenanceLogViewSet,
    MaintenanceTaskViewSet,
    EquipmentDocumentViewSet,
    MaintenancePlanViewSet,
    AuditLogViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'logs', MaintenanceLogViewSet, basename='maintenance-log')
router.register(r'tasks', MaintenanceTaskViewSet, basename='maintenance-task')
router.register(r'documents', EquipmentDocumentViewSet, basename='equipment-document')
router.register(r'plans', MaintenancePlanViewSet, basename='maintenance-plan')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

app_name = 'maintenance_new'

urlpatterns = [
    path('', include(router.urls)),
] 