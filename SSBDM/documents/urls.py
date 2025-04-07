from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document URLs
    path('', views.EquipmentDocumentListView.as_view(), name='document_list'),
    path('<int:pk>/', views.EquipmentDocumentDetailView.as_view(), name='document_detail'),
    path('add/', views.EquipmentDocumentCreateView.as_view(), name='document_add'),
    path('<int:pk>/edit/', views.EquipmentDocumentUpdateView.as_view(), name='document_edit'),
    path('<int:pk>/delete/', views.EquipmentDocumentDeleteView.as_view(), name='document_delete'),
    path('<int:pk>/download/', views.download_document, name='document_download'),
    
    # Document Categories
    path('categories/', views.DocumentCategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.DocumentCategoryDetailView.as_view(), name='category_detail'),
    path('categories/add/', views.DocumentCategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', views.DocumentCategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', views.DocumentCategoryDeleteView.as_view(), name='category_delete'),
] 