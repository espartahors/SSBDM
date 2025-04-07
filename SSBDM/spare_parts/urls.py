from django.urls import path
from . import views

app_name = 'spare_parts'

urlpatterns = [
    # Main list views
    path('', views.spare_part_list, name='spare_part_list'),
    path('categories/', views.category_list, name='category_list'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    
    # Detail views
    path('<int:pk>/', views.spare_part_detail, name='spare_part_detail'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    
    # AJAX Detail Views
    path('ajax/spare-part/<int:pk>/', views.spare_part_detail_ajax, name='spare_part_detail_ajax'),
    path('ajax/category/<int:pk>/', views.category_detail_ajax, name='category_detail_ajax'),
    
    # Create views
    path('add/', views.spare_part_add, name='spare_part_add'),
    path('categories/add/', views.category_add, name='category_add'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    
    # Update views
    path('<int:pk>/update/', views.spare_part_update, name='spare_part_update'),
    path('categories/<int:pk>/update/', views.category_update, name='category_update'),
    path('transactions/<int:pk>/update/', views.transaction_update, name='transaction_update'),
    
    # Delete views
    path('<int:pk>/delete/', views.spare_part_delete, name='spare_part_delete'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    # Additional views
    path('low-stock/', views.low_stock_list, name='low_stock_list'),
    path('stock-dashboard/', views.stock_dashboard, name='stock_dashboard'),
    path('tree-browser/', views.spare_part_tree_browser, name='spare_part_tree_browser'),
    
    # AJAX Tree data
    path('ajax/tree-data/', views.category_tree_data, name='category_tree_data'),
] 