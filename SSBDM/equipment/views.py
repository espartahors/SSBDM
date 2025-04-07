from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from .models import Area, Equipment, TechnicalSpecification
from django.db.models import Q

class AreaListView(LoginRequiredMixin, ListView):
    model = Area
    template_name = 'equipment/area_list.html'
    context_object_name = 'areas'

class AreaDetailView(LoginRequiredMixin, DetailView):
    model = Area
    template_name = 'equipment/area_detail.html'
    context_object_name = 'area'

class AreaCreateView(LoginRequiredMixin, CreateView):
    model = Area
    template_name = 'equipment/area_form.html'
    fields = ['code', 'name', 'parent', 'description']
    success_url = reverse_lazy('equipment:area_list')

class AreaUpdateView(LoginRequiredMixin, UpdateView):
    model = Area
    template_name = 'equipment/area_form.html'
    fields = ['code', 'name', 'parent', 'description']
    success_url = reverse_lazy('equipment:area_list')

class AreaDeleteView(LoginRequiredMixin, DeleteView):
    model = Area
    template_name = 'equipment/area_confirm_delete.html'
    success_url = reverse_lazy('equipment:area_list')

class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = 'equipment/equipment_list.html'
    context_object_name = 'equipment_list'

class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = 'equipment/equipment_detail.html'
    context_object_name = 'equipment'

class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    template_name = 'equipment/equipment_form.html'
    fields = ['code', 'name', 'equipment_type', 'area', 'parent', 'manufacturer', 
             'model', 'serial_number', 'installation_date', 'status', 'description']
    success_url = reverse_lazy('equipment:equipment_list')

class EquipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipment
    template_name = 'equipment/equipment_form.html'
    fields = ['code', 'name', 'equipment_type', 'area', 'parent', 'manufacturer', 
             'model', 'serial_number', 'installation_date', 'status', 'description']
    success_url = reverse_lazy('equipment:equipment_list')

class EquipmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipment
    template_name = 'equipment/equipment_confirm_delete.html'
    success_url = reverse_lazy('equipment:equipment_list')

class TechnicalSpecificationDetailView(LoginRequiredMixin, DetailView):
    model = TechnicalSpecification
    template_name = 'equipment/technical_specs_detail.html'
    context_object_name = 'specs'

class TechnicalSpecificationUpdateView(LoginRequiredMixin, UpdateView):
    model = TechnicalSpecification
    template_name = 'equipment/technical_specs_form.html'
    fields = ['specification', 'value', 'unit']
    success_url = reverse_lazy('equipment:equipment_list')

class TechnicalSpecificationDeleteView(LoginRequiredMixin, DeleteView):
    model = TechnicalSpecification
    template_name = 'equipment/technical_specs_confirm_delete.html'
    context_object_name = 'specification'
    
    def get_success_url(self):
        equipment = self.object.equipment
        return reverse_lazy('equipment:equipment_detail', kwargs={'pk': equipment.pk})

def equipment_tree_data(request):
    """Return JSON data for equipment tree visualization"""
    areas = Area.objects.all()
    equipment = Equipment.objects.all()
    
    data = {
        'areas': [{
            'id': f'area_{area.id}',
            'text': area.name,
            'parent': f'area_{area.parent.id}' if area.parent else '#',
            'type': 'area'
        } for area in areas],
        'equipment': [{
            'id': f'equipment_{eq.id}',
            'text': eq.name,
            'parent': f'area_{eq.area.id}' if eq.area else '#',
            'type': 'equipment'
        } for eq in equipment]
    }
    return JsonResponse(data)

def get_component_detail(request, pk):
    """Return JSON data for a specific equipment component"""
    equipment = get_object_or_404(Equipment, pk=pk)
    data = {
        'name': equipment.name,
        'type': equipment.get_equipment_type_display(),
        'status': equipment.get_status_display(),
        'area': equipment.area.name if equipment.area else None,
        'manufacturer': equipment.manufacturer,
        'model': equipment.model,
        'serial_number': equipment.serial_number,
        'installation_date': equipment.installation_date.strftime('%Y-%m-%d') if equipment.installation_date else None,
        'last_maintenance': equipment.last_maintenance_date.strftime('%Y-%m-%d') if equipment.last_maintenance_date else None,
        'description': equipment.description
    }
    return JsonResponse(data)

def area_tree_data(request):
    """Return JSON data for area tree visualization"""
    areas = Area.objects.all()
    
    # Build tree structure
    if not areas.exists():
        return JsonResponse({'name': 'Areas', 'children': []})
    
    def build_tree(parent=None):
        tree = []
        if parent is None:
            # Get root nodes
            children = Area.objects.filter(parent=None)
        else:
            # Get children of the parent
            children = parent.get_children()
        
        for child in children:
            # Count equipment directly in this area
            equipment_count = child.equipment.count()
            
            node = {
                'name': f"{child.name} ({equipment_count})",
                'id': child.id,
                'code': child.code
            }
            
            # Add children if any
            descendants = child.get_descendants()
            if descendants.exists():
                node['children'] = build_tree(child)
                
            tree.append(node)
            
        return tree
    
    # Start with root nodes (parent=None)
    tree_data = {
        'name': 'Areas',
        'children': build_tree(None)
    }
    
    return JsonResponse(tree_data)

class AreaTreeBrowserView(LoginRequiredMixin, TemplateView):
    """View for browsing areas and equipment in a tree view"""
    template_name = 'equipment/area_tree_browser.html'

def area_detail_partial(request, pk):
    """Returns a partial HTML view of an area's details for AJAX requests"""
    area = get_object_or_404(Area, pk=pk)
    context = {'area': area}
    return render(request, 'equipment/partials/area_detail.html', context)

def equipment_detail_partial(request, pk):
    """Returns a partial HTML view of equipment details for AJAX requests"""
    equipment = get_object_or_404(Equipment, pk=pk)
    context = {'equipment': equipment}
    return render(request, 'equipment/partials/equipment_detail.html', context)

def combined_tree_data(request):
    """Return JSON data for combined areas and equipment tree"""
    # Format for jsTree
    def build_area_tree(parent=None):
        nodes = []
        if parent is None:
            # Get root areas
            areas = Area.objects.filter(parent=None)
        else:
            # Get child areas
            areas = parent.get_children()
        
        for area in areas:
            # Create area node
            area_node = {
                'text': area.name,
                'id': f"area_{area.id}",
                'type': 'area',
                'state': {'opened': False},
                'children': []
            }
            
            # Add sub-areas recursively
            sub_areas = build_area_tree(area)
            if sub_areas:
                area_node['children'].extend(sub_areas)
            
            # Add equipment in this area
            for equipment in area.equipment.filter(parent=None):
                equip_node = build_equipment_node(equipment)
                area_node['children'].append(equip_node)
            
            nodes.append(area_node)
        
        return nodes
    
    def build_equipment_node(equipment):
        # Create equipment node
        equip_node = {
            'text': equipment.name,
            'id': f"equipment_{equipment.id}",
            'type': 'equipment' if equipment.equipment_type != 'component' else 'component',
            'state': {'opened': False}
        }
        
        # Add components recursively
        components = equipment.components.all()
        if components.exists():
            equip_node['children'] = []
            for component in components:
                comp_node = build_equipment_node(component)
                equip_node['children'].append(comp_node)
        
        return equip_node
    
    # Build the tree structure
    tree = build_area_tree(None)
    
    # Add unassigned equipment section if any equipment has no area
    unassigned = Equipment.objects.filter(area=None, parent=None)
    if unassigned.exists():
        unassigned_node = {
            'text': 'Unassigned Equipment',
            'id': 'unassigned',
            'type': 'area',
            'state': {'opened': False},
            'children': []
        }
        
        for equipment in unassigned:
            equip_node = build_equipment_node(equipment)
            unassigned_node['children'].append(equip_node)
        
        tree.append(unassigned_node)
    
    return JsonResponse(tree, safe=False)

@login_required
def add_specification(request, pk):
    """Add a technical specification to equipment"""
    equipment = get_object_or_404(Equipment, pk=pk)
    
    if request.method == 'POST':
        # Create new specification
        spec = TechnicalSpecification(
            equipment=equipment,
            specification=request.POST.get('specification'),
            value=request.POST.get('value'),
            unit=request.POST.get('unit', '')
        )
        spec.save()
        
        # Redirect back to equipment detail
        return redirect('equipment:equipment_detail', pk=equipment.pk)
    
    # If not POST, redirect to equipment detail
    return redirect('equipment:equipment_detail', pk=equipment.pk)

@login_required
def equipment_spare_parts(request, pk):
    """View to display equipment with its related spare parts."""
    equipment = get_object_or_404(Equipment, pk=pk)
    return render(request, 'equipment/partials/equipment_spare_parts.html', {
        'equipment': equipment,
    })

@login_required
def equipment_specs(request, pk):
    """View to display technical specifications for a piece of equipment."""
    equipment = get_object_or_404(Equipment, pk=pk)
    specs = equipment.technical_specifications.all()
    return render(request, 'equipment/partials/equipment_specs.html', {
        'equipment': equipment,
        'specs': specs,
    })

@login_required
def area_tree_browser(request):
    """View for the area tree browser."""
    return render(request, 'equipment/area_tree_browser.html')

@login_required
def equipment_tree_data(request):
    """API view to get equipment hierarchy as JSON for jsTree."""
    equipment_list = Equipment.objects.all().select_related('area', 'parent')
    
    # Build tree nodes
    tree_data = []
    
    # Add equipment nodes
    for equipment in equipment_list:
        parent_id = f"area_{equipment.area.id}" if equipment.area else "#"
        if equipment.parent:
            parent_id = f"equipment_{equipment.parent.id}"
            
        node_type = "component" if equipment.equipment_type == "component" else "equipment"
        
        tree_data.append({
            "id": f"equipment_{equipment.id}",
            "text": equipment.name,
            "parent": parent_id,
            "type": node_type,
            "data": {
                "code": equipment.code,
                "type": equipment.get_equipment_type_display(),
                "status": equipment.get_status_display(),
                "object_type": "equipment",
                "object_id": equipment.id
            }
        })
    
    return JsonResponse(tree_data, safe=False)

@login_required
def tree_data(request):
    """Return JSON data for the jsTree component - areas and equipment"""
    try:
        # Get all areas and equipment organized by parent
        areas = Area.objects.all()
        equipment = Equipment.objects.all()
        
        # Start with root areas (those with no parent)
        tree_data = []
        
        # Add areas first
        for area in areas:
            if area.parent is None:
                # This is a root area
                node = {
                    'id': f'area-{area.id}',
                    'text': f"{area.code} - {area.name}",
                    'type': 'area',
                    'children': _get_area_children(area, areas, equipment)
                }
                tree_data.append(node)
        
        # Add equipment that's not in any area
        for eq in equipment:
            if eq.area is None and eq.parent is None:
                node = {
                    'id': f'equipment-{eq.id}',
                    'text': f"{eq.code} - {eq.name}",
                    'type': 'equipment',
                    'children': _get_equipment_children(eq, equipment)
                }
                tree_data.append(node)
        
        return JsonResponse(tree_data, safe=False)
    except Exception as e:
        # Log the error
        print(f"Error generating tree data: {str(e)}")
        return JsonResponse([], safe=False)

def _get_area_children(parent_area, all_areas, all_equipment):
    """Helper function to recursively build the tree structure for areas"""
    children = []
    
    # Add child areas
    for area in all_areas:
        if area.parent == parent_area:
            node = {
                'id': f'area-{area.id}',
                'text': f"{area.code} - {area.name}",
                'type': 'area',
                'children': _get_area_children(area, all_areas, all_equipment)
            }
            children.append(node)
    
    # Add equipment belonging to this area
    for eq in all_equipment:
        if eq.area == parent_area and eq.parent is None:
            node = {
                'id': f'equipment-{eq.id}',
                'text': f"{eq.code} - {eq.name}",
                'type': 'equipment',
                'children': _get_equipment_children(eq, all_equipment)
            }
            children.append(node)
    
    return children

def _get_equipment_children(parent_equipment, all_equipment):
    """Helper function to recursively build the tree structure for equipment components"""
    children = []
    
    # Add child equipment components
    for eq in all_equipment:
        if eq.parent == parent_equipment:
            node = {
                'id': f'equipment-{eq.id}',
                'text': f"{eq.code} - {eq.name}",
                'type': 'equipment',
                'children': _get_equipment_children(eq, all_equipment)
            }
            children.append(node)
    
    return children

@login_required
def equipment_detail_ajax(request, pk):
    """Return HTML fragment for equipment details in tree browser"""
    try:
        equipment = Equipment.objects.get(pk=pk)
        specifications = equipment.technical_specifications.all()
        components = Equipment.objects.filter(parent=equipment)
        return render(request, 'equipment/partials/equipment_detail_fragment.html', {
            'equipment': equipment,
            'specifications': specifications,
            'components': components
        })
    except Equipment.DoesNotExist:
        return HttpResponse("Equipment not found", status=404)

@login_required
def area_detail_ajax(request, pk):
    """Return HTML fragment for area details in tree browser"""
    try:
        area = Area.objects.get(pk=pk)
        equipment_list = Equipment.objects.filter(area=area, parent=None)
        child_areas = Area.objects.filter(parent=area)
        return render(request, 'equipment/partials/area_detail_fragment.html', {
            'area': area,
            'equipment_list': equipment_list,
            'child_areas': child_areas,
            'equipment_count': equipment_list.count()
        })
    except Area.DoesNotExist:
        return HttpResponse("Area not found", status=404)

@login_required
def equipment_list(request):
    """View for listing equipment with filtering capabilities"""
    equipment = Equipment.objects.all()
    
    # Filter by search term
    search = request.GET.get('search', '')
    if search:
        equipment = equipment.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(manufacturer__icontains=search) |
            Q(model__icontains=search) |
            Q(serial_number__icontains=search)
        )
    
    # Filter by area
    area_id = request.GET.get('area', '')
    if area_id and area_id.isdigit():
        equipment = equipment.filter(area_id=int(area_id))
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        equipment = equipment.filter(status=status)
    
    # Get all areas for filter dropdown
    areas = Area.objects.all()
    
    return render(request, 'equipment/equipment_list.html', {
        'equipment_list': equipment,
        'areas': areas,
        'search': search,
        'selected_area': area_id,
        'selected_status': status
    })

@login_required
def area_list(request):
    """View for listing areas with filtering capabilities"""
    areas = Area.objects.all()
    
    # Filter by search term
    search = request.GET.get('search', '')
    if search:
        areas = areas.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Add equipment count to each area
    for area in areas:
        area.equipment_count = Equipment.objects.filter(area=area).count()
    
    return render(request, 'equipment/area_list.html', {
        'area_list': areas,
        'search': search
    })

@login_required
def equipment_detail(request, pk):
    """View for equipment detail page"""
    equipment = get_object_or_404(Equipment, pk=pk)
    specifications = equipment.technical_specifications.all()
    components = Equipment.objects.filter(parent=equipment)
    
    return render(request, 'equipment/equipment_detail.html', {
        'equipment': equipment,
        'specifications': specifications,
        'components': components
    })

@login_required
def area_detail(request, pk):
    """View for area detail page"""
    area = get_object_or_404(Area, pk=pk)
    equipment_list = Equipment.objects.filter(area=area, parent=None)
    child_areas = Area.objects.filter(parent=area)
    
    return render(request, 'equipment/area_detail.html', {
        'area': area,
        'equipment_list': equipment_list,
        'child_areas': child_areas
    })

@login_required
def equipment_add(request):
    """View for adding equipment"""
    # Redirect to the class-based view
    return EquipmentCreateView.as_view()(request)

@login_required
def area_add(request):
    """View for adding area"""
    # Redirect to the class-based view
    return AreaCreateView.as_view()(request)

@login_required
def equipment_update(request, pk):
    """View for updating equipment"""
    # Redirect to the class-based view
    return EquipmentUpdateView.as_view()(request, pk=pk)

@login_required
def area_update(request, pk):
    """View for updating area"""
    # Redirect to the class-based view
    return AreaUpdateView.as_view()(request, pk=pk)

@login_required
def equipment_delete(request, pk):
    """View for deleting equipment"""
    # Redirect to the class-based view
    return EquipmentDeleteView.as_view()(request, pk=pk)

@login_required
def area_delete(request, pk):
    """View for deleting area"""
    # Redirect to the class-based view
    return AreaDeleteView.as_view()(request, pk=pk)

@login_required
def tree_browser(request):
    """View for equipment tree browser"""
    return render(request, 'equipment/tree_browser.html')

@login_required
def equipment_export_csv(request):
    """Export equipment list as CSV"""
    # Implementation for CSV export
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="equipment.csv"'
    
    # Get filtered equipment
    equipment = Equipment.objects.all()
    
    # Apply the same filters as equipment_list
    search = request.GET.get('search', '')
    if search:
        equipment = equipment.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search) |
            Q(manufacturer__icontains=search) |
            Q(model__icontains=search) |
            Q(serial_number__icontains=search)
        )
    
    area_id = request.GET.get('area', '')
    if area_id and area_id.isdigit():
        equipment = equipment.filter(area_id=int(area_id))
    
    status = request.GET.get('status', '')
    if status:
        equipment = equipment.filter(status=status)
    
    # Create CSV writer
    import csv
    writer = csv.writer(response)
    writer.writerow(['Code', 'Name', 'Type', 'Manufacturer', 'Model', 'Serial Number', 'Area', 'Status', 'Installation Date', 'Last Maintenance'])
    
    for eq in equipment:
        writer.writerow([
            eq.code,
            eq.name,
            eq.get_equipment_type_display(),
            eq.manufacturer,
            eq.model,
            eq.serial_number,
            eq.area.name if eq.area else 'Not Assigned',
            eq.get_status_display(),
            eq.installation_date,
            eq.last_maintenance_date
        ])
    
    return response

@login_required
def equipment_export_excel(request):
    """Export equipment list as Excel"""
    # For simplicity, we'll return CSV format for now
    # A real implementation would use a library like openpyxl or pandas
    return equipment_export_csv(request) 