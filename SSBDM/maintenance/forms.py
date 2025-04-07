from django import forms
from django.contrib.auth.models import User
from mptt.forms import TreeNodeChoiceField
from .models import (
    Area, Equipment, TechnicalSpecification, 
    MaintenanceLog, SparePart, EquipmentDocument
)
import json
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class AreaForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Area.objects.all(), required=False)
    
    class Meta:
        model = Area
        fields = ['code', 'name', 'description', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise ValidationError(_('Area code is required'))
        if len(code) < 3:
            raise ValidationError(_('Area code must be at least 3 characters long'))
        return code.upper()
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError(_('Area name is required'))
        return name.strip()

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'code', 'name', 'equipment_type', 'manufacturer', 
            'model', 'serial_number', 'installation_date', 
            'status', 'description', 'area', 'parent'
        ]
        widgets = {
            'installation_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise ValidationError(_('Equipment code is required'))
        if len(code) < 3:
            raise ValidationError(_('Equipment code must be at least 3 characters long'))
        return code.upper()
    
    def clean_serial_number(self):
        serial_number = self.cleaned_data.get('serial_number')
        if serial_number:
            # Check if serial number is unique
            existing = Equipment.objects.filter(serial_number=serial_number)
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(_('This serial number is already in use'))
        return serial_number
    
    def clean_installation_date(self):
        installation_date = self.cleaned_data.get('installation_date')
        if installation_date and installation_date > timezone.now().date():
            raise ValidationError(_('Installation date cannot be in the future'))
        return installation_date

class TechnicalSpecificationForm(forms.ModelForm):
    # Define form fields for technical specs dynamically
    # These will be converted to JSON and stored in specs_json field
    
    # For Hydraulic System
    oil_tank_capacity = forms.CharField(required=False, label="Oil Tank Capacity")
    max_system_pressure = forms.CharField(required=False, label="Max System Pressure")
    flow_rate = forms.CharField(required=False, label="Flow Rate")
    power_rating = forms.CharField(required=False, label="Power Rating")
    oil_type = forms.CharField(required=False, label="Oil Type")
    operating_temperature = forms.CharField(required=False, label="Operating Temperature")
    
    # For Pumps
    displacement = forms.CharField(required=False, label="Displacement")
    weight = forms.CharField(required=False, label="Weight")
    mounting = forms.CharField(required=False, label="Mounting")
    drive_type = forms.CharField(required=False, label="Drive Type")
    
    class Meta:
        model = TechnicalSpecification
        fields = ['specs_json']
        widgets = {
            'specs_json': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If instance exists, populate form fields from specs_json
        if self.instance.pk:
            try:
                specs = json.loads(self.instance.specs_json)
                for key, value in specs.items():
                    if key in self.fields:
                        self.fields[key].initial = value
            except json.JSONDecodeError:
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Convert form fields to JSON
        specs_json = {}
        for field_name in self.fields:
            if field_name != 'specs_json' and cleaned_data.get(field_name):
                specs_json[field_name] = cleaned_data.get(field_name)
        
        try:
            cleaned_data['specs_json'] = json.dumps(specs_json)
        except json.JSONDecodeError:
            raise ValidationError(_('Invalid JSON data'))
        
        return cleaned_data

class EquipmentWithSpecsForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            'code', 'name', 'equipment_type', 'manufacturer', 
            'model', 'serial_number', 'installation_date', 
            'status', 'description', 'area', 'parent'
        ]
        widgets = {
            'installation_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class MaintenanceLogForm(forms.ModelForm):
    technicians = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = MaintenanceLog
        fields = [
            'equipment', 'title', 'maintenance_type', 
            'description', 'observations', 'date', 'duration', 'technicians'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'observations': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise ValidationError(_('Maintenance date cannot be in the future'))
        return date
    
    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration and duration <= 0:
            raise ValidationError(_('Duration must be greater than 0'))
        return duration

class SparePartForm(forms.ModelForm):
    class Meta:
        model = SparePart
        fields = [
            'part_number', 'description', 'quantity_in_stock', 
            'minimum_stock', 'cost', 'location', 'supplier', 'equipment'
        ]
        widgets = {
            'equipment': forms.CheckboxSelectMultiple(),
        }
    
    def clean_quantity_in_stock(self):
        quantity = self.cleaned_data.get('quantity_in_stock')
        if quantity < 0:
            raise ValidationError(_('Quantity cannot be negative'))
        return quantity
    
    def clean_minimum_stock(self):
        minimum = self.cleaned_data.get('minimum_stock')
        if minimum < 0:
            raise ValidationError(_('Minimum stock cannot be negative'))
        return minimum
    
    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost and cost < 0:
            raise ValidationError(_('Cost cannot be negative'))
        return cost

class EquipmentDocumentForm(forms.ModelForm):
    class Meta:
        model = EquipmentDocument
        fields = ['equipment', 'title', 'document_type', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError(_('File size cannot exceed 10MB'))
            
            # Check file type
            allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
            if file.content_type not in allowed_types:
                raise ValidationError(_('File type not supported. Please upload PDF, Word, or image files only'))
        
        return file

class EquipmentSearchForm(forms.Form):
    search = forms.CharField(required=False, label='', 
                            widget=forms.TextInput(attrs={'placeholder': 'Search equipment...'}))
    
    def clean_search(self):
        search = self.cleaned_data.get('search')
        if search and len(search) < 2:
            raise ValidationError(_('Search term must be at least 2 characters long'))
        return search.strip()