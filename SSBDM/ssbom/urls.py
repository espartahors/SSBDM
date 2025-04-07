from django.urls import path
from . import views

app_name = 'ssbom'

urlpatterns = [
    # Main browser view
    path('', views.ssbom_browser, name='browser'),
    
    # Relationship management
    path('relationships/', views.manage_relationships, name='manage_relationships'),
    path('relationships/get/', views.get_equipment_relationships, name='get_equipment_relationships'),
    path('relationships/save/', views.save_relationship, name='save_relationship'),
    path('relationships/delete/', views.delete_relationship, name='delete_relationship'),
    
    # AJAX endpoints for tree data
    path('tree-data/', views.tree_data, name='tree_data'),
    
    # AJAX endpoints for detail views
    path('area/<int:pk>/detail/', views.area_detail_ajax, name='area_detail_ajax'),
    path('equipment/<int:pk>/detail/', views.equipment_detail_ajax, name='equipment_detail_ajax'),
    path('spare-part/<int:pk>/detail/', views.spare_part_detail_ajax, name='spare_part_detail_ajax'),
    path('document/<int:pk>/detail/', views.document_detail_ajax, name='document_detail_ajax'),
    path('category/<int:pk>/detail/', views.category_detail_ajax, name='category_detail_ajax'),
] 