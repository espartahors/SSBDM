from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (
    Area, Equipment, TechnicalSpecification, 
    MaintenanceLog, SparePart, EquipmentDocument, MaintenanceTask
)

@admin.register(Area)
class AreaAdmin(MPTTModelAdmin):
    list_display = ('code', 'name', 'parent')
    list_filter = ('parent',)
    search_fields = ('code', 'name')

class TechnicalSpecificationInline(admin.StackedInline):
    model = TechnicalSpecification
    can_delete = False

class EquipmentDocumentInline(admin.TabularInline):
    model = EquipmentDocument
    extra = 1

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'equipment_type', 'status', 'area', 'parent')
    list_filter = ('status', 'area', 'equipment_type')
    search_fields = ('code', 'name', 'serial_number')
    inlines = [TechnicalSpecificationInline, EquipmentDocumentInline]

class MaintenanceTaskInline(admin.TabularInline):
    model = MaintenanceTask
    extra = 0
    fields = ('description', 'status', 'assigned_to', 'due_date')
    readonly_fields = ('completed_date',)

class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'maintenance_type', 'date', 'duration', 'created_by')
    list_filter = ('maintenance_type', 'date', 'created_by')
    search_fields = ('equipment__code', 'equipment__name', 'title')
    ordering = ('-date',)
    inlines = [MaintenanceTaskInline]
    readonly_fields = ('created_at', 'created_by')
    
    fieldsets = (
        ('Maintenance Details', {
            'fields': ('equipment', 'title', 'maintenance_type', 'description')
        }),
        ('Execution', {
            'fields': ('date', 'duration', 'technicians', 'observations')
        }),
        ('Audit', {
            'fields': ('created_at', 'created_by'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('maintenance_log', 'status', 'assigned_to', 'due_date', 'completed_date')
    list_filter = ('status', 'assigned_to', 'due_date')
    search_fields = ('maintenance_log__equipment__code', 'description')
    ordering = ('status', 'due_date')
    readonly_fields = ('completed_date',)
    
    fieldsets = (
        ('Task Details', {
            'fields': ('maintenance_log', 'description', 'status')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'due_date', 'completed_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )

@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'description', 'quantity_in_stock', 'minimum_stock')
    list_filter = ('quantity_in_stock', 'supplier')
    search_fields = ('part_number', 'description', 'supplier')
    filter_horizontal = ('equipment',)

@admin.register(EquipmentDocument)
class EquipmentDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'equipment', 'document_type', 'upload_date')
    list_filter = ('document_type', 'upload_date')
    search_fields = ('title', 'equipment__code', 'equipment__name')

admin.site.register(MaintenanceLog, MaintenanceLogAdmin)
admin.site.register(MaintenanceTask, MaintenanceTaskAdmin)