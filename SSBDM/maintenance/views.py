from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from .models import (
    Area, Equipment, TechnicalSpecification, 
    MaintenanceLog, SparePart, EquipmentDocument
)
from .forms import (
    AreaForm, EquipmentForm, TechnicalSpecificationForm, 
    MaintenanceLogForm, SparePartForm, EquipmentDocumentForm,
    EquipmentWithSpecsForm, EquipmentSearchForm
)
import json
from django.db import models


def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    area = self.get_object()
    context['operational_equipment_count'] = area.equipment.filter(status='operational').count()
    return context

@login_required
def dashboard(request):
    """Main dashboard view"""
    equipment_count = Equipment.objects.count()
    maintenance_count = MaintenanceLog.objects.count()
    upcoming_maintenance = MaintenanceLog.objects.all().order_by('date')[:5]
    low_stock_parts = SparePart.objects.filter(
        quantity_in_stock__lt=models.F('minimum_stock')
    )[:5]
    
    context = {
        'equipment_count': equipment_count,
        'maintenance_count': maintenance_count,
        'upcoming_maintenance': upcoming_maintenance,
        'low_stock_parts': low_stock_parts,
    }
    return render(request, 'maintenance/dashboard.html', context)

class AreaListView(LoginRequiredMixin, ListView):
    model = Area
    context_object_name = 'areas'
    template_name = 'maintenance/area_list.html'

class AreaDetailView(LoginRequiredMixin, DetailView):
    model = Area
    context_object_name = 'area'
    template_name = 'maintenance/area_detail.html'

class AreaCreateView(LoginRequiredMixin, CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'maintenance/area_form.html'
    success_url = reverse_lazy('maintenance:area_list')

class AreaUpdateView(LoginRequiredMixin, UpdateView):
    model = Area
    form_class = AreaForm
    template_name = 'maintenance/area_form.html'
    success_url = reverse_lazy('maintenance:area_list')

class AreaDeleteView(LoginRequiredMixin, DeleteView):
    model = Area
    context_object_name = 'area'
    template_name = 'maintenance/area_confirm_delete.html'
    success_url = reverse_lazy('maintenance:area_list')

class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    context_object_name = 'equipment_list'
    template_name = 'maintenance/equipment_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = EquipmentSearchForm(self.request.GET or None)
        context['areas'] = Area.objects.all()
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_form = EquipmentSearchForm(self.request.GET or None)
        
        if search_form.is_valid():
            search_term = search_form.cleaned_data.get('search')
            if search_term:
                queryset = queryset.filter(
                    Q(code__icontains=search_term) | 
                    Q(name__icontains=search_term) |
                    Q(equipment_type__icontains=search_term)
                )
                
        return queryset

class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    context_object_name = 'equipment'
    template_name = 'maintenance/equipment_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = self.get_object()
        
        # Get technical specifications
        try:
            tech_specs = equipment.technical_specs
            context['tech_specs'] = json.loads(tech_specs.specs_json)
        except TechnicalSpecification.DoesNotExist:
            context['tech_specs'] = {}
        
        # Get maintenance logs
        context['maintenance_logs'] = equipment.maintenance_logs.all()[:5]
        
        # Get components (sub-equipment)
        context['components'] = equipment.components.all()
        
        # Get spare parts
        context['spare_parts'] = equipment.spare_parts.all()
        
        # Get documents
        context['documents'] = equipment.documents.all()
        
        return context

class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'maintenance/equipment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['specs_form'] = TechnicalSpecificationForm(self.request.POST)
        else:
            context['specs_form'] = TechnicalSpecificationForm()
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        specs_form = context['specs_form']
        
        if form.is_valid() and specs_form.is_valid():
            equipment = form.save()
            specs = specs_form.save(commit=False)
            specs.equipment = equipment
            specs.save()
            messages.success(self.request, f"Equipment {equipment.code} created successfully!")
            return redirect(equipment.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class EquipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'maintenance/equipment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        equipment = self.get_object()
        
        if self.request.POST:
            try:
                specs = equipment.technical_specs
                context['specs_form'] = TechnicalSpecificationForm(self.request.POST, instance=specs)
            except TechnicalSpecification.DoesNotExist:
                context['specs_form'] = TechnicalSpecificationForm(self.request.POST)
        else:
            try:
                specs = equipment.technical_specs
                context['specs_form'] = TechnicalSpecificationForm(instance=specs)
            except TechnicalSpecification.DoesNotExist:
                context['specs_form'] = TechnicalSpecificationForm()
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        specs_form = context['specs_form']
        equipment = self.get_object()
        
        if form.is_valid() and specs_form.is_valid():
            equipment = form.save()
            
            # Handle technical specs
            try:
                specs = equipment.technical_specs
                specs_form = TechnicalSpecificationForm(self.request.POST, instance=specs)
                specs = specs_form.save()
            except TechnicalSpecification.DoesNotExist:
                specs = specs_form.save(commit=False)
                specs.equipment = equipment
                specs.save()
            
            messages.success(self.request, f"Equipment {equipment.code} updated successfully!")
            return redirect(equipment.get_absolute_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

class EquipmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Equipment
    context_object_name = 'equipment'
    template_name = 'maintenance/equipment_confirm_delete.html'
    success_url = reverse_lazy('maintenance:equipment_list')
    
    def delete(self, request, *args, **kwargs):
        equipment = self.get_object()
        messages.success(request, f"Equipment {equipment.code} deleted successfully!")
        return super().delete(request, *args, **kwargs)

class MaintenanceLogListView(LoginRequiredMixin, ListView):
    model = MaintenanceLog
    context_object_name = 'maintenance_logs'
    template_name = 'maintenance/maintenance_log_list.html'
    paginate_by = 10

class MaintenanceLogDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceLog
    context_object_name = 'log'
    template_name = 'maintenance/maintenance_log_detail.html'

class MaintenanceLogCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = 'maintenance/maintenance_log_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        equipment_id = self.request.GET.get('equipment')
        if equipment_id:
            initial['equipment'] = equipment_id
        return initial
    
    def form_valid(self, form):
        maintenance_log = form.save()
        messages.success(self.request, "Maintenance log created successfully!")
        
        # Check if redirecting back to equipment page
        if 'equipment' in self.request.GET:
            equipment_id = self.request.GET.get('equipment')
            return redirect('maintenance:equipment_detail', pk=equipment_id)
        
        return redirect(maintenance_log.get_absolute_url())

class MaintenanceLogUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceLog
    form_class = MaintenanceLogForm
    template_name = 'maintenance/maintenance_log_form.html'

class MaintenanceLogDeleteView(LoginRequiredMixin, DeleteView):
    model = MaintenanceLog
    context_object_name = 'log'
    template_name = 'maintenance/maintenance_log_confirm_delete.html'
    
    def get_success_url(self):
        equipment_id = self.object.equipment.id
        return reverse_lazy('maintenance:equipment_detail', kwargs={'pk': equipment_id})

class SparePartListView(LoginRequiredMixin, ListView):
    model = SparePart
    context_object_name = 'spare_parts'
    template_name = 'maintenance/spare_part_list.html'

class SparePartDetailView(LoginRequiredMixin, DetailView):
    model = SparePart
    context_object_name = 'spare_part'
    template_name = 'maintenance/spare_part_detail.html'

class SparePartCreateView(LoginRequiredMixin, CreateView):
    model = SparePart
    form_class = SparePartForm
    template_name = 'maintenance/spare_part_form.html'

class SparePartUpdateView(LoginRequiredMixin, UpdateView):
    model = SparePart
    form_class = SparePartForm
    template_name = 'maintenance/spare_part_form.html'

class SparePartDeleteView(LoginRequiredMixin, DeleteView):
    model = SparePart
    context_object_name = 'spare_part'
    template_name = 'maintenance/spare_part_confirm_delete.html'
    success_url = reverse_lazy('maintenance:spare_part_list')

class DocumentListView(LoginRequiredMixin, ListView):
    model = EquipmentDocument
    context_object_name = 'documents'
    template_name = 'maintenance/document_list.html'

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = EquipmentDocument
    context_object_name = 'document'
    template_name = 'maintenance/document_detail.html'

class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = EquipmentDocument
    form_class = EquipmentDocumentForm
    template_name = 'maintenance/document_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        equipment_id = self.request.GET.get('equipment')
        if equipment_id:
            initial['equipment'] = equipment_id
        return initial
    
    def form_valid(self, form):
        document = form.save()
        messages.success(self.request, "Document uploaded successfully!")
        
        # Check if redirecting back to equipment page
        if 'equipment' in self.request.GET:
            equipment_id = self.request.GET.get('equipment')
            return redirect('maintenance:equipment_detail', pk=equipment_id)
        
        return redirect(document.get_absolute_url())

class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = EquipmentDocument
    form_class = EquipmentDocumentForm
    template_name = 'maintenance/document_form.html'

class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = EquipmentDocument
    context_object_name = 'document'
    template_name = 'maintenance/document_confirm_delete.html'
    
    def get_success_url(self):
        equipment_id = self.object.equipment.id
        return reverse_lazy('maintenance:equipment_detail', kwargs={'pk': equipment_id})

@login_required
def equipment_tree_data(request):
    """Return JSON data for the equipment tree"""
    areas = Area.objects.all()
    equipment = Equipment.objects.all()
    
    # Build tree structure
    tree_data = [{"id": f"area_{area.id}", 
                  "parent": f"area_{area.parent_id}" if area.parent else "#",
                  "text": f"{area.code} - {area.name}",
                  "type": "area"} for area in areas]
    
    # Add equipment nodes
    for eq in equipment:
        if eq.parent:
            parent = f"equipment_{eq.parent_id}"
        else:
            parent = f"area_{eq.area_id}"
        
        tree_data.append({
            "id": f"equipment_{eq.id}",
            "parent": parent,
            "text": f"{eq.code} - {eq.name}",
            "type": "equipment"
        })
    
    return JsonResponse(tree_data, safe=False)

@login_required
def get_component_detail(request, pk):
    """AJAX view to get component details"""
    component = get_object_or_404(Equipment, pk=pk)
    
    # Basic info
    data = {
        'id': component.id,
        'code': component.code,
        'name': component.name,
        'type': component.equipment_type,
        'manufacturer': component.manufacturer,
        'model': component.model,
        'serial_number': component.serial_number,
        'installation_date': component.installation_date.strftime('%Y-%m-%d') if component.installation_date else '',
        'last_maintenance_date': component.last_maintenance_date.strftime('%Y-%m-%d') if component.last_maintenance_date else '',
        'status': component.status,
    }
    
    # Technical specs
    try:
        tech_specs = component.technical_specs
        data['tech_specs'] = json.loads(tech_specs.specs_json)
    except TechnicalSpecification.DoesNotExist:
        data['tech_specs'] = {}
    
    # Maintenance history (last 3)
    maintenance_logs = component.maintenance_logs.all().order_by('-date')[:3]
    data['maintenance_logs'] = [{
        'id': log.id,
        'title': log.title,
        'type': log.maintenance_type,
        'date': log.date.strftime('%Y-%m-%d'),
        'technicians': ', '.join([tech.username for tech in log.technicians.all()])
    } for log in maintenance_logs]
    
    # Spare parts
    spare_parts = component.spare_parts.all()
    data['spare_parts'] = [{
        'id': part.id,
        'part_number': part.part_number,
        'description': part.description,
        'quantity': part.quantity_in_stock,
        'status': part.stock_status()
    } for part in spare_parts]
    
    return JsonResponse(data)