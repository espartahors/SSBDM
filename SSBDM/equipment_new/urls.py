from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EquipmentViewSet,
    AreaViewSet,
    TechnicalSpecificationViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'areas', AreaViewSet, basename='area')
router.register(r'technical-specs', TechnicalSpecificationViewSet, basename='technical-spec')

app_name = 'equipment_new'

urlpatterns = [
    path('', include(router.urls)),
] 