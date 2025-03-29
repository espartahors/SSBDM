from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Areas
    path('areas/', views.AreaListView.as_view(), name='area_list'),
    path('areas/<int:pk>/', views.AreaDetailView.as_view(), name='area_detail'),
    path('areas/new/', views.AreaCreateView.as_view(), name='area_create'),
    path('areas/<int:pk>/edit/', views.AreaUpdateView.as_view(), name='area_update'),
    path('areas/<int:pk>/delete/', views.AreaDeleteView.as_view(), name='area_delete'),
    
    # Equipment
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('equipment/new/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:pk>/edit/', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('equipment/<int:pk>/delete/', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
    
    # Maintenance Logs
    path('maintenance-logs/', views.MaintenanceLogListView.as_view(), name='maintenance_log_list'),
    path('maintenance-logs/<int:pk>/', views.MaintenanceLogDetailView.as_view(), name='maintenance_log_detail'),
    path('maintenance-logs/new/', views.MaintenanceLogCreateView.as_view(), name='maintenance_log_create'),
    path('maintenance-logs/<int:pk>/edit/', views.MaintenanceLogUpdateView.as_view(), name='maintenance_log_update'),
    path('maintenance-logs/<int:pk>/delete/', views.MaintenanceLogDeleteView.as_view(), name='maintenance_log_delete'),
    
    # Spare Parts
    path('spare-parts/', views.SparePartListView.as_view(), name='spare_part_list'),
    path('spare-parts/<int:pk>/', views.SparePartDetailView.as_view(), name='spare_part_detail'),
    path('spare-parts/new/', views.SparePartCreateView.as_view(), name='spare_part_create'),
    path('spare-parts/<int:pk>/edit/', views.SparePartUpdateView.as_view(), name='spare_part_update'),
    path('spare-parts/<int:pk>/delete/', views.SparePartDeleteView.as_view(), name='spare_part_delete'),
    
    # Documents
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('documents/new/', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/edit/', views.DocumentUpdateView.as_view(), name='document_update'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    
    # AJAX API endpoints
    path('api/equipment-tree/', views.equipment_tree_data, name='equipment_tree_data'),
    path('api/component/<int:pk>/', views.get_component_detail, name='get_component_detail'),
]