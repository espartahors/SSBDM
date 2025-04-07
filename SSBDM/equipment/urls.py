from django.urls import path
from . import views

app_name = 'equipment'

urlpatterns = [
    # Main list views
    path('', views.equipment_list, name='equipment_list'),
    path('areas/', views.area_list, name='area_list'),
    
    # Detail views
    path('<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('areas/<int:pk>/', views.area_detail, name='area_detail'),
    
    # AJAX Detail Views
    path('ajax/equipment/<int:pk>/', views.equipment_detail_ajax, name='equipment_detail_ajax'),
    path('ajax/area/<int:pk>/', views.area_detail_ajax, name='area_detail_ajax'),
    
    # Create views
    path('add/', views.equipment_add, name='equipment_add'),
    path('areas/add/', views.area_add, name='area_add'),
    
    # Update views
    path('<int:pk>/update/', views.equipment_update, name='equipment_update'),
    path('areas/<int:pk>/update/', views.area_update, name='area_update'),
    
    # Delete views
    path('<int:pk>/delete/', views.equipment_delete, name='equipment_delete'),
    path('areas/<int:pk>/delete/', views.area_delete, name='area_delete'),
    
    # Additional views
    path('tree-browser/', views.tree_browser, name='tree_browser'),
    
    # Export views
    path('export/csv/', views.equipment_export_csv, name='equipment_export_csv'),
    path('export/excel/', views.equipment_export_excel, name='equipment_export_excel'),
    
    # AJAX Tree data
    path('ajax/tree-data/', views.tree_data, name='tree_data'),
] 