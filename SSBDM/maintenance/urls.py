from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    # Maintenance Log URLs
    path('logs/', views.MaintenanceLogListView.as_view(), name='log_list'),
    path('logs/<int:pk>/', views.MaintenanceLogDetailView.as_view(), name='log_detail'),
    path('logs/add/', views.MaintenanceLogCreateView.as_view(), name='log_add'),
    path('logs/<int:pk>/edit/', views.MaintenanceLogUpdateView.as_view(), name='log_edit'),
    path('logs/<int:pk>/delete/', views.MaintenanceLogDeleteView.as_view(), name='log_delete'),
    
    # Maintenance Task URLs
    path('tasks/', views.MaintenanceTaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', views.MaintenanceTaskDetailView.as_view(), name='task_detail'),
    path('tasks/add/', views.MaintenanceTaskCreateView.as_view(), name='task_add'),
    path('tasks/<int:pk>/edit/', views.MaintenanceTaskUpdateView.as_view(), name='task_edit'),
    path('tasks/<int:pk>/delete/', views.MaintenanceTaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<int:pk>/complete/', views.complete_task, name='task_complete'),
    
    # Dashboard and Reports
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.reports, name='reports'),
    path('reports/maintenance-summary/', views.maintenance_summary_report, name='maintenance_summary'),
    path('reports/equipment-status/', views.equipment_status_report, name='equipment_status'),
    
    # AJAX API endpoints
    path('api/equipment-tree/', views.equipment_tree_data, name='equipment_tree_data'),
    path('api/component/<int:pk>/', views.get_component_detail, name='get_component_detail'),
    
    # Audit Log
    path('audit-log/', views.audit_log, name='audit_log'),
]