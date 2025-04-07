from django.contrib import admin
from django.db.models import F, Q
from .models import SparePart, SparePartTransaction, Category
from mptt.admin import MPTTModelAdmin

class StockStatusFilter(admin.SimpleListFilter):
    title = 'Stock Status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock'),
            ('low_stock', 'Low Stock'),
            ('out_of_stock', 'Out of Stock'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(current_stock__gte=F('minimum_stock'))
        elif self.value() == 'low_stock':
            return queryset.filter(
                current_stock__lt=F('minimum_stock'),
                current_stock__gt=0
            )
        elif self.value() == 'out_of_stock':
            return queryset.filter(current_stock=0)

class SparePartTransactionInline(admin.TabularInline):
    model = SparePartTransaction
    extra = 0
    fields = ['transaction_type', 'quantity', 'date', 'equipment', 'notes']
    readonly_fields = ['date']

@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'code', 'description')
    search_fields = ('name', 'code', 'description')
    list_filter = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'parent', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SparePart)
class SparePartAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'current_stock', 'minimum_stock', 'price', 'location', 'supplier', 'stock_status_display')
    list_filter = ('category', StockStatusFilter, 'supplier', 'manufacturer')
    search_fields = ('code', 'name', 'description', 'supplier', 'manufacturer')
    inlines = [SparePartTransactionInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description', 'category', 'location', 'image')
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'minimum_stock', 'unit', 'price', 'currency')
        }),
        ('Supplier Details', {
            'fields': ('supplier', 'supplier_reference', 'manufacturer', 'lead_time')
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

    def stock_status_display(self, obj):
        status = obj.stock_status
        if status == 'in_stock':
            return 'In Stock'
        elif status == 'low_stock':
            return 'Low Stock'
        elif status == 'out_of_stock':
            return 'Out of Stock'
        return status
    stock_status_display.short_description = 'Stock Status'

    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SparePartTransaction)
class SparePartTransactionAdmin(admin.ModelAdmin):
    list_display = ['spare_part', 'transaction_type', 'quantity', 'date', 'equipment', 'created_by']
    list_filter = ['transaction_type', 'date', 'equipment']
    search_fields = ['spare_part__code', 'spare_part__name', 'notes', 'reference']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('spare_part', 'transaction_type', 'quantity', 'unit_price', 'equipment', 'notes', 'reference')
        }),
        ('Metadata', {
            'fields': ('date', 'created_at', 'created_by'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change) 