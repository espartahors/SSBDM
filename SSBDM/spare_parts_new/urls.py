from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    SparePartViewSet,
    SparePartTransactionViewSet
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'parts', SparePartViewSet, basename='spare-part')
router.register(r'transactions', SparePartTransactionViewSet, basename='transaction')

app_name = 'spare_parts_new'

urlpatterns = [
    path('', include(router.urls)),
] 