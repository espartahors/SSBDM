from django.contrib import admin
from .models import DocumentCategory, EquipmentDocument

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(EquipmentDocument)
class EquipmentDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'equipment', 'document_type', 'uploaded_by', 'upload_date', 'is_active')
    list_filter = ('document_type', 'category', 'upload_date', 'is_active')
    search_fields = ('title', 'equipment__name', 'description', 'document_number')
    date_hierarchy = 'upload_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'equipment', 'document_type', 'category', 'description')
        }),
        ('Document Details', {
            'fields': ('file', 'thumbnail', 'document_number', 'revision', 'issue_date', 'expiry_date', 'is_confidential')
        }),
        ('Additional Information', {
            'fields': ('notes', 'is_active')
        }),
        ('Metadata', {
            'fields': ('upload_date', 'updated_at', 'uploaded_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('upload_date', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.uploaded_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change) 