from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _
from .models import (
    Area, Equipment, TechnicalSpecification, 
    MaintenanceLog, SparePart, EquipmentDocument, AuditLog, MaintenanceTask
)
from .forms import (
    AreaForm, EquipmentForm, TechnicalSpecificationForm, 
    MaintenanceLogForm, SparePartForm, EquipmentDocumentForm,
    EquipmentWithSpecsForm, EquipmentSearchForm
)
from .permissions import get_user_role
import json
from django.db import models
from django.utils import timezone


def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    area = self.get_object()
    context['operational_equipment_count'] = area.equipment.filter(status='operational').count()
    return context

@login_required
def dashboard(request):
    """Main dashboard view"""
    try:
        # Equipment statistics
        equipment_count = Equipment.objects.count()
        operational_count = Equipment.objects.filter(status='operational').count()
        maintenance_count = Equipment.objects.filter(status='maintenance').count()
        out_of_service_count = Equipment.objects.filter(status='out_of_service').count()
        
        # Calculate percentages
        operational_percentage = round((operational_count / equipment_count * 100)) if equipment_count > 0 else 0
        maintenance_percentage = round((maintenance_count / equipment_count * 100)) if equipment_count > 0 else 0
        out_of_service_percentage = round((out_of_service_count / equipment_count * 100)) if equipment_count > 0 else 0
        
        # Task statistics
        active_tasks = MaintenanceTask.objects.filter(status='pending').count()
        completed_tasks = MaintenanceTask.objects.filter(status='completed').count()
        
        # Recent maintenance logs and upcoming tasks
        recent_logs = MaintenanceLog.objects.order_by('-date')[:5]
        upcoming_tasks = MaintenanceTask.objects.filter(status='pending').order_by('due_date')[:5]
        
        # Monthly maintenance activities data for chart
        now = timezone.now()
        six_months_ago = now - timezone.timedelta(days=180)
        
        # Get maintenance logs for the last 6 months
        maintenance_logs = MaintenanceLog.objects.filter(
            date__gte=six_months_ago
        ).order_by('date')
        
        # Prepare data for monthly activities chart
        months = []
        monthly_activities = []
        
        # Get the last 6 months
        for i in range(5, -1, -1):
            month = now - timezone.timedelta(days=30 * i)
            month_name = month.strftime('%b')
            months.append(month_name)
            
            # Count logs for this month
            month_start = month.replace(day=1)
            if i > 0:
                next_month = now - timezone.timedelta(days=30 * (i-1))
                month_end = next_month.replace(day=1)
            else:
                month_end = now
            
            count = maintenance_logs.filter(date__gte=month_start, date__lt=month_end).count()
            monthly_activities.append(count)
        
        # Equipment by type data for pie chart
        equipment_types = []
        equipment_type_counts = []
        
        # Get equipment types and counts
        for choice in Equipment.EQUIPMENT_TYPE_CHOICES:
            type_code = choice[0]
            type_name = choice[1]
            count = Equipment.objects.filter(equipment_type=type_code).count()
            if count > 0:  # Only include types that have equipment
                equipment_types.append(type_name)
                equipment_type_counts.append(count)
        
        context = {
            'equipment_count': equipment_count,
            'operational_count': operational_count,
            'maintenance_count': maintenance_count,
            'out_of_service_count': out_of_service_count,
            'operational_percentage': operational_percentage,
            'maintenance_percentage': maintenance_percentage,
            'out_of_service_percentage': out_of_service_percentage,
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
            'recent_logs': recent_logs,
            'upcoming_tasks': upcoming_tasks,
            'months': json.dumps(months),
            'monthly_activities': json.dumps(monthly_activities),
            'equipment_types': json.dumps(equipment_types),
            'equipment_type_counts': json.dumps(equipment_type_counts),
        }
        return render(request, 'maintenance/dashboard.html', context)
    except Exception as e:
        messages.error(request, _(f'An error occurred while loading the dashboard: {str(e)}'))
        return render(request, 'maintenance/dashboard.html', {})

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
    
    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, _('Area created successfully'))
            return response
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, _('An error occurred while creating the area'))
            return self.form_invalid(form)

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
        
        # Remove or simplify the technical specs handling
        context['tech_specs'] = {} # Empty dict instead of trying to access technical_specs
        
        # Keep the rest of the method as is
        context['maintenance_logs'] = equipment.maintenance_logs.all()[:5]
        context['components'] = equipment.components.all()
        context['spare_parts'] = equipment.spare_parts.all()
        context['documents'] = equipment.documents.all()
        
        return context

class EquipmentCreateView(LoginRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'maintenance/equipment_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        area_id = self.request.GET.get('area')
        parent_id = self.request.GET.get('parent')
        
        if area_id:
            initial['area'] = area_id
        if parent_id:
            initial['parent'] = parent_id
            
        return initial
    
    @transaction.atomic
    def form_valid(self, form):
        try:
            equipment = form.save()
            messages.success(self.request, _('Equipment created successfully'))
            return redirect(equipment.get_absolute_url())
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, _('An error occurred while creating the equipment'))
            return self.form_invalid(form)

class EquipmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = 'maintenance/equipment_form.html'
    
    def form_valid(self, form):
        equipment = form.save()
        messages.success(self.request, f"Equipment {equipment.code} updated successfully!")
        return redirect(equipment.get_absolute_url())

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
    template_name = 'maintenance/maintenance_list.html'
    context_object_name = 'maintenance_logs'
    ordering = ['-date']

class MaintenanceLogDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceLog
    template_name = 'maintenance/maintenance_detail.html'
    context_object_name = 'maintenance_log'

class MaintenanceLogCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceLog
    template_name = 'maintenance/maintenance_form.html'
    fields = ['equipment', 'maintenance_type', 'title', 'description', 'date', 'duration', 'technicians', 'observations']
    success_url = reverse_lazy('maintenance:maintenance_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class MaintenanceLogUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceLog
    template_name = 'maintenance/maintenance_form.html'
    fields = ['equipment', 'maintenance_type', 'title', 'description', 'date', 'duration', 'technicians', 'observations']
    success_url = reverse_lazy('maintenance:maintenance_list')

class MaintenanceLogDeleteView(LoginRequiredMixin, DeleteView):
    model = MaintenanceLog
    template_name = 'maintenance/maintenance_confirm_delete.html'
    success_url = reverse_lazy('maintenance:maintenance_list')

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
    
    @transaction.atomic
    def form_valid(self, form):
        try:
            spare_part = form.save()
            messages.success(self.request, _('Spare part created successfully'))
            return redirect(spare_part.get_absolute_url())
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, _('An error occurred while creating the spare part'))
            return self.form_invalid(form)

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
    
    @transaction.atomic
    def form_valid(self, form):
        try:
            document = form.save()
            messages.success(self.request, _('Document uploaded successfully'))
            return redirect(document.get_absolute_url())
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, _('An error occurred while uploading the document'))
            return self.form_invalid(form)

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
    try:
        equipment = Equipment.objects.all()
        data = []
        
        for item in equipment:
            data.append({
                'id': item.id,
                'text': f"{item.code} - {item.name}",
                'parent': item.parent.id if item.parent else '#',
                'type': 'equipment'
            })
        
        return JsonResponse(data, safe=False)
    except Exception as e:
        return HttpResponseBadRequest(_('Error loading equipment tree data'))

@login_required
def get_component_detail(request, pk):
    try:
        component = get_object_or_404(Equipment, pk=pk)
        data = {
            'name': component.name,
            'code': component.code,
            'status': component.status,
            'description': component.description,
        }
        return JsonResponse(data)
    except Exception as e:
        return HttpResponseBadRequest(_('Error loading component details'))

@login_required
@permission_required('maintenance.view_auditlog', raise_exception=True)
def audit_log(request):
    logs = AuditLog.objects.all().order_by('-timestamp')
    user_role = get_user_role(request.user)
    
    context = {
        'logs': logs,
        'user_role': user_role,
    }
    return render(request, 'maintenance/audit_log.html', context)

class MaintenanceTaskListView(LoginRequiredMixin, ListView):
    model = MaintenanceTask
    template_name = 'maintenance/task_list.html'
    context_object_name = 'tasks'
    ordering = ['-due_date']

class MaintenanceTaskDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceTask
    template_name = 'maintenance/task_detail.html'
    context_object_name = 'task'

class MaintenanceTaskCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceTask
    template_name = 'maintenance/task_form.html'
    fields = ['maintenance_log', 'description', 'status', 'assigned_to', 'due_date', 'notes']
    success_url = reverse_lazy('maintenance:task_list')

class MaintenanceTaskUpdateView(LoginRequiredMixin, UpdateView):
    model = MaintenanceTask
    template_name = 'maintenance/task_form.html'
    fields = ['maintenance_log', 'description', 'status', 'assigned_to', 'due_date', 'notes']
    success_url = reverse_lazy('maintenance:task_list')

class MaintenanceTaskDeleteView(LoginRequiredMixin, DeleteView):
    model = MaintenanceTask
    template_name = 'maintenance/task_confirm_delete.html'
    success_url = reverse_lazy('maintenance:task_list')

@login_required
def complete_task(request, pk):
    task = get_object_or_404(MaintenanceTask, pk=pk)
    task.status = 'completed'
    task.completed_date = timezone.now()
    task.save()
    return redirect('maintenance:task_detail', pk=task.pk)

@login_required
def reports(request):
    return render(request, 'maintenance/reports.html')

@login_required
def maintenance_summary_report(request):
    maintenance_logs = MaintenanceLog.objects.all()
    context = {
        'maintenance_logs': maintenance_logs
    }
    return render(request, 'maintenance/reports/maintenance_summary.html', context)

@login_required
def equipment_status_report(request):
    equipment = Equipment.objects.all()
    context = {
        'equipment': equipment
    }
    return render(request, 'maintenance/reports/equipment_status.html', context)