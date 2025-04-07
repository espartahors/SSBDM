from django.contrib import admin
from .models import BOMRelationship, BOMChangeLog, EquipmentHierarchy, EquipmentSparePartUsage


@admin.register(BOMRelationship)
class BOMRelationshipAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'related_item', 'relationship_type', 'quantity', 'criticality')
    list_filter = ('relationship_type', 'criticality', 'equipment__area', 'equipment')
    search_fields = ('equipment__name', 'spare_part__name', 'document__title', 'related_equipment__name', 'notes')
    autocomplete_fields = ['equipment', 'spare_part', 'document', 'related_equipment']
    
    def related_item(self, obj):
        if obj.spare_part:
            return f"Spare Part: {obj.spare_part.name}"
        elif obj.document:
            return f"Document: {obj.document.title}"
        elif obj.related_equipment:
            return f"Equipment: {obj.related_equipment.name}"
        return "None"
    related_item.short_description = "Related Item"
    
    fieldsets = (
        ('Equipment', {
            'fields': ('equipment',)
        }),
        ('Related Item', {
            'fields': ('spare_part', 'document', 'related_equipment'),
            'description': 'Select only one of these options.',
        }),
        ('Relationship Details', {
            'fields': ('relationship_type', 'quantity', 'position', 'criticality', 'notes')
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


@admin.register(EquipmentSparePartUsage)
class EquipmentSparePartUsageAdmin(admin.ModelAdmin):
    list_display = ('spare_part', 'equipment', 'status', 'installation_date', 'removal_date', 'serial_number')
    list_filter = ('status', 'installation_date', 'equipment__area', 'equipment')
    search_fields = ('spare_part__name', 'equipment__name', 'serial_number', 'lot_number', 'notes')
    date_hierarchy = 'installation_date'
    
    fieldsets = (
        ('Equipment & Part', {
            'fields': ('equipment', 'spare_part', 'relationship')
        }),
        ('Usage Details', {
            'fields': ('status', 'installation_date', 'removal_date', 'position', 'serial_number', 'lot_number')
        }),
        ('Replacement Chain', {
            'fields': ('replaced_by',),
            'classes': ('collapse',),
        }),
        ('Additional Information', {
            'fields': ('notes',)
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


@admin.register(BOMChangeLog)
class BOMChangeLogAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'action', 'relationship', 'timestamp', 'user')
    list_filter = ('action', 'timestamp', 'user')
    search_fields = ('equipment__name', 'description')
    date_hierarchy = 'timestamp'
    readonly_fields = ('relationship', 'equipment', 'action', 'description', 
                       'previous_state', 'new_state', 'timestamp', 'user')
    
    fieldsets = (
        ('Change Details', {
            'fields': ('relationship', 'equipment', 'action', 'description')
        }),
        ('State Details', {
            'fields': ('previous_state', 'new_state'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('timestamp', 'user'),
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EquipmentHierarchy)
class EquipmentHierarchyAdmin(admin.ModelAdmin):
    list_display = ('ancestor', 'descendant', 'path_length')
    list_filter = ('path_length', 'ancestor__area')
    search_fields = ('ancestor__name', 'descendant__name')
    readonly_fields = ('ancestor', 'descendant', 'path_length', 'relationship_path', 'updated_at')
    
    fieldsets = (
        ('Hierarchy Details', {
            'fields': ('ancestor', 'descendant', 'path_length')
        }),
        ('Path Information', {
            'fields': ('relationship_path', 'updated_at'),
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False 