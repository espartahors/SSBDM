from django.contrib import admin
from .models import SparePart, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'current_stock', 'minimum_stock', 'location', 'stock_status')
    list_filter = ('category', 'unit')
    search_fields = ('code', 'name', 'manufacturer', 'supplier', 'supplier_reference')
    autocomplete_fields = ['category'] 