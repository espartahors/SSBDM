from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from maintenance.models import (
    Area, Equipment, TechnicalSpecification, 
    MaintenanceLog, SparePart, EquipmentDocument
)
import json
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Generates test data for the maintenance system'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating test data...'))
        
        # Create superuser if none exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS('Created admin user (username: admin, password: admin)'))
        
        # Create technicians
        technicians = []
        technician_names = [
            ('john.doe', 'John', 'Doe'),
            ('jane.smith', 'Jane', 'Smith'),
            ('robert.johnson', 'Robert', 'Johnson'),
            ('sarah.williams', 'Sarah', 'Williams'),
        ]
        
        for username, first, last in technician_names:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username, 
                    email=f'{username}@example.com',
                    password='password',
                    first_name=first,
                    last_name=last
                )
                technicians.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created technician: {username}'))
        
        if not technicians:
            technicians = User.objects.filter(is_superuser=False)
        
        # Create plant areas
            # Top level areas
            area_asu = Area.objects.create(code='ASU', name='Air Separation Unit')
            area_ftp = Area.objects.create(code='FTP', name='Fume Treatment Plant')
            area_wtp = Area.objects.create(code='WTP', name='Water Treatment Plant')
            area_ccm = Area.objects.create(code='CCM', name='Continuous Casting Machine')
            area_smp = Area.objects.create(code='SMP', name='Steel Melting Plant')
            
            # Subareas
            Area.objects.create(code='CMP', name='Compression System', parent=area_asu)
            Area.objects.create(code='DST', name='Distillation System', parent=area_asu)
            Area.objects.create(code='PUR', name='Purification Unit', parent=area_asu)
            
            Area.objects.create(code='BAG', name='Bag Filter System', parent=area_ftp)
            Area.objects.create(code='FAN', name='Main Extraction Fans', parent=area_ftp)
            
            Area.objects.create(code='PMP', name='Pumping Station', parent=area_wtp)
            Area.objects.create(code='FLT', name='Filtration System', parent=area_wtp)
            
            Area.objects.create(code='MOL', name='Mold Oscillation', parent=area_ccm)
            Area.objects.create(code='WCS', name='Water Cooling System', parent=area_ccm)
            
            area_eaf = Area.objects.create(code='EAF', name='Electric Arc Furnace', parent=area_smp)
            Area.objects.create(code='LF', name='Ladle Furnace', parent=area_smp)
            
            self.stdout.write(self.style.SUCCESS('Created plant areas'))
            
            # Create equipment in the EAF area
            equipment_hyd = Equipment.objects.create(
                code='SMP-EAF-HYD-0001',
                name='Hydraulic System',
                equipment_type='Hydraulic System',
                manufacturer='Rexroth',
                model='HSP-500-T',
                serial_number='RX2345678',
                installation_date=date(2021, 9, 10),
                last_maintenance_date=date(2024, 10, 15),
                status='operational',
                area=area_eaf
            )
            
            # Technical specifications for hydraulic system
            specs = {
                'oil_tank_capacity': '500 L',
                'max_system_pressure': '315 bar',
                'flow_rate': '350 L/min',
                'power_rating': '110 kW',
                'oil_type': 'ISO VG 46',
                'operating_temperature': '-10°C to +80°C'
            }
            TechnicalSpecification.objects.create(
                equipment=equipment_hyd,
                specs_json=json.dumps(specs)
            )
            
            # Create components
            pump = Equipment.objects.create(
                code='SMP-EAF-HYD-PMP-0001',
                name='Main Hydraulic Pump',
                equipment_type='Pump',
                manufacturer='Rexroth',
                model='A10VSO 100 DFR1/31R-PPA12N00',
                serial_number='R902400326',
                installation_date=date(2022, 5, 15),
                last_maintenance_date=date(2024, 11, 2),
                status='operational',
                area=area_eaf,
                parent=equipment_hyd
            )
            
            # Technical specifications for pump
            pump_specs = {
                'displacement': '100 cm³/rev',
                'max_system_pressure': '280 bar',
                'flow_rate': '180 L/min @ 1800 rpm',
                'operating_temperature': '-20°C to +80°C',
                'weight': '55 kg',
                'mounting': 'Flange mounting',
                'drive_type': 'Electric Motor Driven'
            }
            TechnicalSpecification.objects.create(
                equipment=pump,
                specs_json=json.dumps(pump_specs)
            )
            
            valve = Equipment.objects.create(
                code='SMP-EAF-HYD-VLV-0001',
                name='Pressure Relief Valve',
                equipment_type='Valve',
                manufacturer='Rexroth',
                model='DBDH10K1X/315',
                serial_number='R900425722',
                installation_date=date(2022, 5, 15),
                last_maintenance_date=date(2024, 8, 12),
                status='operational',
                area=area_eaf,
                parent=equipment_hyd
            )
            
            # Create maintenance logs
            maintenance_types = ['preventive', 'corrective', 'predictive', 'emergency']
            maintenance_titles = [
                'Quarterly inspection and oil analysis',
                'Replaced pressure relief valve',
                'Monthly routine check',
                'Fixed oil leak',
                'Changed filter elements',
                'Adjusted pressure settings',
                'Emergency repair after pressure spike',
                'Calibration of sensors'
            ]
            
            # Create 10 maintenance logs
            for i in range(10):
                days_ago = random.randint(0, 365)
                maint_date = date.today() - timedelta(days=days_ago)
                maint_type = random.choice(maintenance_types)
                equipment = random.choice([equipment_hyd, pump, valve])
                
                log = MaintenanceLog.objects.create(
                    equipment=equipment,
                    title=random.choice(maintenance_titles),
                    maintenance_type=maint_type,
                    description=f"Performed {maint_type} maintenance on {equipment.name}.",
                    findings="All parameters within normal range." if maint_type == 'preventive' else "Fixed issue and restored normal operation.",
                    date=maint_date,
                    duration=random.randint(1, 8)
                )
                
                # Add 1-3 random technicians
                num_techs = random.randint(1, min(3, len(technicians)))
                for tech in random.sample(list(technicians), num_techs):
                    log.technicians.add(tech)
            
            # Create spare parts
            spare_parts = [
                {
                    'part_number': 'SMP-EAF-HYD-SPR-0012',
                    'description': 'Shaft Seal Kit',
                    'quantity_in_stock': 3,
                    'minimum_stock': 2,
                    'equipment': [pump]
                },
                {
                    'part_number': 'SMP-EAF-HYD-SPR-0015',
                    'description': 'Valve Plate',
                    'quantity_in_stock': 1,
                    'minimum_stock': 2,
                    'equipment': [pump]
                },
                {
                    'part_number': 'SMP-EAF-HYD-SPR-0018',
                    'description': 'Piston Set',
                    'quantity_in_stock': 0,
                    'minimum_stock': 1,
                    'equipment': [pump]
                },
                {
                    'part_number': 'SMP-EAF-HYD-SPR-0022',
                    'description': 'Filter Element',
                    'quantity_in_stock': 5,
                    'minimum_stock': 3,
                    'equipment': [equipment_hyd]
                },
                {
                    'part_number': 'SMP-EAF-HYD-SPR-0025',
                    'description': 'Pressure Relief Spring',
                    'quantity_in_stock': 2,
                    'minimum_stock': 2,
                    'equipment': [valve]
                }
            ]
            
            for part_data in spare_parts:
                equipment_list = part_data.pop('equipment')
                part = SparePart.objects.create(**part_data)
                for eq in equipment_list:
                    part.equipment.add(eq)
            
            self.stdout.write(self.style.SUCCESS('Created sample equipment, components, maintenance logs, and spare parts'))
        else:
            self.stdout.write(self.style.WARNING('Areas already exist, skipping test data creation'))