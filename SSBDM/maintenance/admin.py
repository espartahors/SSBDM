from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (
    Area, Equipment, TechnicalSpecification, 
    MaintenanceLog, SparePart, EquipmentDocument
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

@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'equipment', 'maintenance_type', 'date', 'duration')
    list_filter = ('maintenance_type', 'date', 'equipment')
    search_fields = ('title', 'description', 'equipment__code', 'equipment__name')
    filter_horizontal = ('technicians',)
    date_hierarchy = 'date'

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