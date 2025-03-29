from django import forms
from django.contrib.auth.models import User
from mptt.forms import TreeNodeChoiceField
from .models import (
    Area, Equipment, TechnicalSpecification, 
    MaintenanceLog, SparePart, EquipmentDocument
)
import json

class AreaForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Area.objects.all(), required=False)
    
    class Meta:
        model = Area
        fields = ['code', 'name', 'description', 'parent']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

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
            specs = json.loads(self.instance.specs_json)
            for key, value in specs.items():
                if key in self.fields:
                    self.fields[key].initial = value
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Convert form fields to JSON
        specs_json = {}
        for field_name in self.fields:
            if field_name != 'specs_json' and cleaned_data.get(field_name):
                specs_json[field_name] = cleaned_data.get(field_name)
        
        cleaned_data['specs_json'] = json.dumps(specs_json)
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
            'description', 'findings', 'date', 'duration', 'technicians'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'findings': forms.Textarea(attrs={'rows': 3}),
        }

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

class EquipmentDocumentForm(forms.ModelForm):
    class Meta:
        model = EquipmentDocument
        fields = ['equipment', 'title', 'document_type', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class EquipmentSearchForm(forms.Form):
    search = forms.CharField(required=False, label='', 
                            widget=forms.TextInput(attrs={'placeholder': 'Search equipment...'}))