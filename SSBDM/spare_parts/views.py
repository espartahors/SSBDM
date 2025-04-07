from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from .models import SparePart, SparePartTransaction
from django.http import JsonResponse
from equipment_new.models import Equipment, Area
from .models import Category

class SparePartListView(LoginRequiredMixin, ListView):
    model = SparePart
    template_name = 'spare_parts/spare_part_list.html'
    context_object_name = 'spare_parts'
    ordering = ['part_number']

class SparePartDetailView(LoginRequiredMixin, DetailView):
    model = SparePart
    template_name = 'spare_parts/spare_part_detail.html'
    context_object_name = 'spare_part'

class SparePartCreateView(LoginRequiredMixin, CreateView):
    model = SparePart
    template_name = 'spare_parts/spare_part_form.html'
    fields = ['part_number', 'description', 'equipment', 'quantity_in_stock', 
             'minimum_stock', 'location', 'supplier', 'cost']
    success_url = reverse_lazy('spare_parts:spare_part_list')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

class SparePartUpdateView(LoginRequiredMixin, UpdateView):
    model = SparePart
    template_name = 'spare_parts/spare_part_form.html'
    fields = ['part_number', 'description', 'equipment', 'quantity_in_stock', 
             'minimum_stock', 'location', 'supplier', 'cost']
    success_url = reverse_lazy('spare_parts:spare_part_list')

class SparePartDeleteView(LoginRequiredMixin, DeleteView):
    model = SparePart
    template_name = 'spare_parts/spare_part_confirm_delete.html'
    success_url = reverse_lazy('spare_parts:spare_part_list')

class SparePartTransactionListView(LoginRequiredMixin, ListView):
    model = SparePartTransaction
    template_name = 'spare_parts/transaction_list.html'
    context_object_name = 'transactions'
    ordering = ['-date']

class SparePartTransactionDetailView(LoginRequiredMixin, DetailView):
    model = SparePartTransaction
    template_name = 'spare_parts/transaction_detail.html'
    context_object_name = 'transaction'

class SparePartTransactionCreateView(LoginRequiredMixin, CreateView):
    model = SparePartTransaction
    template_name = 'spare_parts/transaction_form.html'
    fields = ['spare_part', 'transaction_type', 'quantity', 'notes']
    success_url = reverse_lazy('spare_parts:transaction_list')

    def form_valid(self, form):
        form.instance.performed_by = self.request.user
        transaction = form.save(commit=False)
        
        # Update stock quantity based on transaction type
        if transaction.transaction_type == 'in':
            transaction.spare_part.quantity_in_stock += transaction.quantity
        else:  # 'out'
            transaction.spare_part.quantity_in_stock -= transaction.quantity
        
        transaction.spare_part.save()
        transaction.save()
        return super().form_valid(form)

class SparePartTransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = SparePartTransaction
    template_name = 'spare_parts/transaction_form.html'
    fields = ['spare_part', 'transaction_type', 'quantity', 'notes']
    success_url = reverse_lazy('spare_parts:transaction_list')

class SparePartTransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = SparePartTransaction
    template_name = 'spare_parts/transaction_confirm_delete.html'
    success_url = reverse_lazy('spare_parts:transaction_list')

class LowStockListView(LoginRequiredMixin, ListView):
    model = SparePart
    template_name = 'spare_parts/stock_list.html'
    context_object_name = 'spare_parts'
    
    def get_queryset(self):
        return SparePart.objects.filter(quantity_in_stock__lt=F('minimum_stock'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Low Stock Items'
        return context

class StockDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'spare_parts/stock_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_parts'] = SparePart.objects.count()
        context['low_stock'] = SparePart.objects.filter(quantity_in_stock__lt=F('minimum_stock')).count()
        context['out_of_stock'] = SparePart.objects.filter(quantity_in_stock=0).count()
        context['recent_transactions'] = SparePartTransaction.objects.order_by('-date')[:5]
        return context

@login_required
def stock_dashboard(request):
    total_parts = SparePart.objects.count()
    low_stock = SparePart.objects.filter(quantity_in_stock__lt=F('minimum_stock')).count()
    out_of_stock = SparePart.objects.filter(quantity_in_stock=0).count()
    recent_transactions = SparePartTransaction.objects.order_by('-date')[:5]

    context = {
        'total_parts': total_parts,
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
        'recent_transactions': recent_transactions
    }
    return render(request, 'spare_parts/stock_dashboard.html', context)

@login_required
def low_stock_list(request):
    spare_parts = SparePart.objects.filter(quantity_in_stock__lt=F('minimum_stock'))
    context = {
        'spare_parts': spare_parts,
        'title': 'Low Stock Items'
    }
    return render(request, 'spare_parts/stock_list.html', context)

@login_required
def out_of_stock_list(request):
    spare_parts = SparePart.objects.filter(quantity_in_stock=0)
    context = {
        'spare_parts': spare_parts,
        'title': 'Out of Stock Items'
    }
    return render(request, 'spare_parts/stock_list.html', context)

@login_required
def reorder_list(request):
    spare_parts = SparePart.objects.filter(
        Q(quantity_in_stock__lt=F('minimum_stock')) | Q(quantity_in_stock=0)
    ).order_by('quantity_in_stock')
    context = {
        'spare_parts': spare_parts,
        'title': 'Items to Reorder'
    }
    return render(request, 'spare_parts/stock_list.html', context)

@login_required
def spare_part_tree_browser(request):
    """View for the spare parts tree browser."""
    return render(request, 'spare_parts/spare_part_tree_browser.html')

@login_required
def spare_parts_tree_data(request):
    """API view to get spare parts hierarchy as JSON for jsTree."""
    # Get all relevant data
    areas = Area.objects.all()
    equipment = Equipment.objects.all().select_related('area', 'parent')
    spare_parts = SparePart.objects.all().select_related('equipment', 'category')
    categories = Category.objects.all()
    
    # Build tree nodes
    tree_data = []
    
    # Add area nodes
    for area in areas:
        parent_id = f"area_{area.parent.id}" if area.parent else "#"
        tree_data.append({
            "id": f"area_{area.id}",
            "text": area.name,
            "parent": parent_id,
            "type": "area",
            "data": {
                "object_type": "area",
                "object_id": area.id
            }
        })
    
    # Add equipment nodes
    for eq in equipment:
        parent_id = f"area_{eq.area.id}" if eq.area else "#"
        if eq.parent:
            parent_id = f"equipment_{eq.parent.id}"
            
        node_type = "component" if eq.equipment_type == "component" else "equipment"
        
        tree_data.append({
            "id": f"equipment_{eq.id}",
            "text": eq.name,
            "parent": parent_id,
            "type": node_type,
            "data": {
                "code": eq.code,
                "type": eq.get_equipment_type_display(),
                "status": eq.get_status_display(),
                "object_type": "equipment",
                "object_id": eq.id
            }
        })
    
    # Add category nodes
    for category in categories:
        parent_id = f"category_{category.parent.id}" if category.parent else "#"
        tree_data.append({
            "id": f"category_{category.id}",
            "text": category.name,
            "parent": parent_id,
            "type": "category",
            "data": {
                "object_type": "category",
                "object_id": category.id
            }
        })
    
    # Add spare part nodes
    for part in spare_parts:
        if part.equipment:
            parent_id = f"equipment_{part.equipment.id}"
        elif part.category:
            parent_id = f"category_{part.category.id}"
        else:
            parent_id = "#"
            
        tree_data.append({
            "id": f"spare_part_{part.id}",
            "text": part.description,
            "parent": parent_id,
            "type": "spare_part",
            "data": {
                "part_number": part.part_number,
                "quantity": part.quantity_in_stock,
                "status": part.get_stock_status_display(),
                "object_type": "spare_part",
                "object_id": part.id
            }
        })
    
    return JsonResponse(tree_data, safe=False)

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'spare_parts/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(parent=None)

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'spare_parts/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['spare_parts'] = self.object.spare_parts.all()
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    template_name = 'spare_parts/category_form.html'
    fields = ['name', 'description', 'parent']
    success_url = reverse_lazy('spare_parts:category_list')

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    template_name = 'spare_parts/category_form.html'
    fields = ['name', 'description', 'parent']
    success_url = reverse_lazy('spare_parts:category_list')
    
    def get_success_url(self):
        return reverse_lazy('spare_parts:category_detail', kwargs={'pk': self.object.pk})

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'spare_parts/category_confirm_delete.html'
    success_url = reverse_lazy('spare_parts:category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if category has spare parts or subcategories
        context['has_spare_parts'] = self.object.spare_parts.exists()
        context['has_subcategories'] = self.object.get_children().exists()
        return context 

@login_required
def category_tree_data(request):
    """Return JSON data for the jsTree component - categories and spare parts"""
    try:
        # Get all categories organized by parent
        categories = Category.objects.all()
        spare_parts = SparePart.objects.all()
        
        # Start with root categories (those with no parent)
        tree_data = []
        
        # Add categories first
        for category in categories:
            if category.parent is None:
                # This is a root category
                node = {
                    'id': f'category-{category.id}',
                    'text': category.name,
                    'type': 'category',
                    'children': _get_category_children(category, categories, spare_parts)
                }
                tree_data.append(node)
        
        return JsonResponse(tree_data, safe=False)
    except Exception as e:
        # Log the error
        print(f"Error generating tree data: {str(e)}")
        return JsonResponse([], safe=False)

def _get_category_children(parent_category, all_categories, all_spare_parts):
    """Helper function to recursively build the tree structure"""
    children = []
    
    # Add child categories
    for category in all_categories:
        if category.parent == parent_category:
            node = {
                'id': f'category-{category.id}',
                'text': category.name,
                'type': 'category',
                'children': _get_category_children(category, all_categories, all_spare_parts)
            }
            children.append(node)
    
    # Add spare parts belonging to this category
    for part in all_spare_parts:
        if part.category == parent_category:
            node = {
                'id': f'sparepart-{part.id}',
                'text': f"{part.part_number} - {part.description[:30]}{'...' if len(part.description) > 30 else ''}",
                'type': 'sparepart',
                'children': False
            }
            children.append(node)
    
    return children

@login_required
def spare_part_detail_ajax(request, pk):
    """Return HTML fragment for spare part details in tree browser"""
    try:
        spare_part = SparePart.objects.get(pk=pk)
        return render(request, 'spare_parts/partials/spare_part_detail_fragment.html', {
            'spare_part': spare_part
        })
    except SparePart.DoesNotExist:
        return HttpResponse("Spare part not found", status=404)

@login_required
def category_detail_ajax(request, pk):
    """Return HTML fragment for category details in tree browser"""
    try:
        category = Category.objects.get(pk=pk)
        spare_parts = SparePart.objects.filter(category=category)
        return render(request, 'spare_parts/partials/category_detail_fragment.html', {
            'category': category,
            'spare_parts': spare_parts,
            'spare_parts_count': spare_parts.count()
        })
    except Category.DoesNotExist:
        return HttpResponse("Category not found", status=404)

@login_required
def spare_part_list(request):
    """View for listing spare parts with filtering capabilities"""
    spare_parts = SparePart.objects.all().order_by('part_number')
    
    # Filter by search term
    search = request.GET.get('search', '')
    if search:
        spare_parts = spare_parts.filter(
            Q(part_number__icontains=search) |
            Q(description__icontains=search) |
            Q(supplier__icontains=search) |
            Q(location__icontains=search)
        )
    
    # Filter by equipment
    equipment_id = request.GET.get('equipment', '')
    if equipment_id and equipment_id.isdigit():
        spare_parts = spare_parts.filter(equipment_id=int(equipment_id))
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id and category_id.isdigit():
        spare_parts = spare_parts.filter(category_id=int(category_id))
    
    # Filter by stock status
    stock_status = request.GET.get('stock_status', '')
    if stock_status == 'low':
        spare_parts = spare_parts.filter(quantity_in_stock__lt=F('minimum_stock'))
    elif stock_status == 'out':
        spare_parts = spare_parts.filter(quantity_in_stock=0)
    
    # Get all equipment and categories for filter dropdowns
    equipment_list = Equipment.objects.all()
    categories = Category.objects.all()
    
    return render(request, 'spare_parts/spare_part_list.html', {
        'spare_parts': spare_parts,
        'equipment_list': equipment_list,
        'categories': categories,
        'search': search,
        'selected_equipment': equipment_id,
        'selected_category': category_id,
        'selected_stock_status': stock_status
    })

@login_required
def category_list(request):
    """View for listing spare part categories with filtering capabilities"""
    categories = Category.objects.all()
    
    # Filter by search term
    search = request.GET.get('search', '')
    if search:
        categories = categories.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Add part count to each category
    for category in categories:
        category.part_count = SparePart.objects.filter(category=category).count()
    
    return render(request, 'spare_parts/category_list.html', {
        'categories': categories,
        'search': search
    })

@login_required
def transaction_list(request):
    """View for listing spare part transactions with filtering capabilities"""
    transactions = SparePartTransaction.objects.all().order_by('-date')
    
    # Filter by search term
    search = request.GET.get('search', '')
    if search:
        transactions = transactions.filter(
            Q(spare_part__part_number__icontains=search) |
            Q(spare_part__description__icontains=search) |
            Q(notes__icontains=search)
        )
    
    # Filter by transaction type
    transaction_type = request.GET.get('transaction_type', '')
    if transaction_type in ['in', 'out']:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)
    
    return render(request, 'spare_parts/transaction_list.html', {
        'transactions': transactions,
        'search': search,
        'selected_transaction_type': transaction_type,
        'date_from': date_from,
        'date_to': date_to
    })

@login_required
def spare_part_detail(request, pk):
    """View for spare part detail page"""
    spare_part = get_object_or_404(SparePart, pk=pk)
    transactions = SparePartTransaction.objects.filter(spare_part=spare_part).order_by('-date')
    
    return render(request, 'spare_parts/spare_part_detail.html', {
        'spare_part': spare_part,
        'transactions': transactions
    })

@login_required
def category_detail(request, pk):
    """View for category detail page"""
    category = get_object_or_404(Category, pk=pk)
    spare_parts = SparePart.objects.filter(category=category)
    subcategories = Category.objects.filter(parent=category)
    
    return render(request, 'spare_parts/category_detail.html', {
        'category': category,
        'spare_parts': spare_parts,
        'subcategories': subcategories
    })

@login_required
def transaction_detail(request, pk):
    """View for transaction detail page"""
    transaction = get_object_or_404(SparePartTransaction, pk=pk)
    
    return render(request, 'spare_parts/transaction_detail.html', {
        'transaction': transaction
    })

@login_required
def spare_part_add(request):
    """View for adding spare part - redirects to class-based view"""
    return SparePartCreateView.as_view()(request)

@login_required
def category_add(request):
    """View for adding category - redirects to class-based view"""
    return CategoryCreateView.as_view()(request)

@login_required
def transaction_add(request):
    """View for adding transaction - redirects to class-based view"""
    return SparePartTransactionCreateView.as_view()(request)

@login_required
def spare_part_update(request, pk):
    """View for updating spare part - redirects to class-based view"""
    return SparePartUpdateView.as_view()(request, pk=pk)

@login_required
def category_update(request, pk):
    """View for updating category - redirects to class-based view"""
    return CategoryUpdateView.as_view()(request, pk=pk)

@login_required
def transaction_update(request, pk):
    """View for updating transaction - redirects to class-based view"""
    return SparePartTransactionUpdateView.as_view()(request, pk=pk)

@login_required
def spare_part_delete(request, pk):
    """View for deleting spare part - redirects to class-based view"""
    return SparePartDeleteView.as_view()(request, pk=pk)

@login_required
def category_delete(request, pk):
    """View for deleting category - redirects to class-based view"""
    return CategoryDeleteView.as_view()(request, pk=pk)

@login_required
def transaction_delete(request, pk):
    """View for deleting transaction - redirects to class-based view"""
    return SparePartTransactionDeleteView.as_view()(request, pk=pk) 