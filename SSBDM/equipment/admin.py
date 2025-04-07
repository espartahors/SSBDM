from django.contrib import admin
from .models import Area, Equipment, TechnicalSpecification
from mptt.admin import MPTTModelAdmin

@admin.register(Area)
class AreaAdmin(MPTTModelAdmin):
    list_display = ('code', 'name', 'parent')
    list_filter = ('parent',)
    search_fields = ('code', 'name', 'description')
    ordering = ('code',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'parent', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

class EquipmentInline(admin.TabularInline):
    model = Equipment
    extra = 0
    fields = ('code', 'name', 'equipment_type', 'status')
    readonly_fields = ('code', 'name', 'equipment_type', 'status')
    fk_name = 'parent'

class TechnicalSpecificationInline(admin.StackedInline):
    model = TechnicalSpecification
    extra = 0

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'equipment_type', 'area', 'status', 'last_maintenance_date', 'is_critical')
    list_filter = ('equipment_type', 'status', 'area', 'is_critical')
    search_fields = ('code', 'name', 'serial_number', 'description')
    ordering = ('code',)
    inlines = [TechnicalSpecificationInline, EquipmentInline]
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'equipment_type', 'area', 'parent')
        }),
        ('Technical Details', {
            'fields': ('manufacturer', 'model', 'serial_number', 'installation_date', 'is_critical')
        }),
        ('Status Information', {
            'fields': ('status', 'last_maintenance_date', 'next_maintenance_date', 'maintenance_interval')
        }),
        ('Financial Information', {
            'fields': ('purchase_date', 'purchase_cost', 'warranty_expiration', 'expected_lifetime'),
            'classes': ('collapse',),
        }),
        ('Additional Information', {
            'fields': ('description', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(TechnicalSpecification)
class TechnicalSpecificationAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'specification', 'value', 'unit')
    list_filter = ('equipment',)
    search_fields = ('specification', 'value', 'equipment__name')
    
    fieldsets = (
        ('Specification Details', {
            'fields': ('equipment', 'specification', 'value', 'unit')
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