from django.contrib import admin
from .models import Equipment, Area

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent')
    list_filter = ('parent',)
    search_fields = ('name', 'code')
    autocomplete_fields = ['parent']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'equipment_type', 'area', 'status')
    list_filter = ('equipment_type', 'status', 'area')
    search_fields = ('code', 'name', 'manufacturer', 'model', 'serial_number')
    autocomplete_fields = ['area', 'parent'] 