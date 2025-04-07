#!/usr/bin/env python
import os
import sys
import random
import datetime
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSBDM.settings')
import django
django.setup()

# Import models
from django.contrib.auth.models import User
from equipment_new.models import Area, Equipment, TechnicalSpecification
from maintenance.models import MaintenanceLog, MaintenanceTask

print("Creating dummy data for SSBDM...")

# Get or create admin user for assignments
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Created admin user")

# Create technicians
def create_technicians():
    technicians = []
    if not User.objects.filter(username='jsmith').exists():
        technicians.append(User.objects.create_user('jsmith', 'john.smith@example.com', 'password', 
                                                 first_name='John', last_name='Smith'))
    else:
        technicians.append(User.objects.get(username='jsmith'))
        
    if not User.objects.filter(username='mjohnson').exists():
        technicians.append(User.objects.create_user('mjohnson', 'mike.johnson@example.com', 'password', 
                                                  first_name='Mike', last_name='Johnson'))
    else:
        technicians.append(User.objects.get(username='mjohnson'))
        
    if not User.objects.filter(username='rbrown').exists():
        technicians.append(User.objects.create_user('rbrown', 'robert.brown@example.com', 'password', 
                                                  first_name='Robert', last_name='Brown'))
    else:
        technicians.append(User.objects.get(username='rbrown'))
        
    if not User.objects.filter(username='dlee').exists():
        technicians.append(User.objects.create_user('dlee', 'david.lee@example.com', 'password', 
                                                 first_name='David', last_name='Lee'))
    else:
        technicians.append(User.objects.get(username='dlee'))
        
    if not User.objects.filter(username='swilliams').exists():
        technicians.append(User.objects.create_user('swilliams', 'sarah.williams@example.com', 'password', 
                                                  first_name='Sarah', last_name='Williams'))
    else:
        technicians.append(User.objects.get(username='swilliams'))
        
    if not User.objects.filter(username='aturner').exists():
        technicians.append(User.objects.create_user('aturner', 'alex.turner@example.com', 'password', 
                                                 first_name='Alex', last_name='Turner'))
    else:
        technicians.append(User.objects.get(username='aturner'))
        
    print(f"Created or retrieved {len(technicians)} technicians")
    return {
        'jsmith': technicians[0],
        'mjohnson': technicians[1],
        'rbrown': technicians[2],
        'dlee': technicians[3],
        'swilliams': technicians[4],
        'aturner': technicians[5]
    }

# Create areas and sub-areas
def create_areas():
    areas_dict = {}
    
    # Main areas - check if they exist first
    if not Area.objects.filter(code="PROD").exists():
        production = Area.objects.create(
            code="PROD",
            name="Production Facility",
            description="Main production area for steel manufacturing"
        )
    else:
        production = Area.objects.get(code="PROD")
    areas_dict['production'] = production
    
    if not Area.objects.filter(code="WH").exists():
        warehouse = Area.objects.create(
            code="WH",
            name="Warehouse",
            description="Storage area for raw materials and finished products"
        )
    else:
        warehouse = Area.objects.get(code="WH")
    areas_dict['warehouse'] = warehouse
    
    if not Area.objects.filter(code="MAINT").exists():
        maintenance_area = Area.objects.create(
            code="MAINT",
            name="Maintenance Department",
            description="Central maintenance and repair facility"
        )
    else:
        maintenance_area = Area.objects.get(code="MAINT")
    areas_dict['maintenance'] = maintenance_area
    
    if not Area.objects.filter(code="OFF").exists():
        office = Area.objects.create(
            code="OFF",
            name="Administrative Offices",
            description="Management and administrative departments"
        )
    else:
        office = Area.objects.get(code="OFF")
    areas_dict['office'] = office
    
    # Sub-areas
    # Production sub-areas
    if not Area.objects.filter(code="PROD-MLT").exists():
        melting = Area.objects.create(
            code="PROD-MLT",
            name="Melting Area",
            description="Area for melting raw materials",
            parent=production
        )
    else:
        melting = Area.objects.get(code="PROD-MLT")
    areas_dict['melting'] = melting
    
    if not Area.objects.filter(code="PROD-CST").exists():
        casting = Area.objects.create(
            code="PROD-CST",
            name="Casting Area",
            description="Area for casting molten metal",
            parent=production
        )
    else:
        casting = Area.objects.get(code="PROD-CST")
    areas_dict['casting'] = casting
    
    if not Area.objects.filter(code="PROD-ROL").exists():
        rolling = Area.objects.create(
            code="PROD-ROL",
            name="Rolling Mill",
            description="Area for hot and cold rolling of steel",
            parent=production
        )
    else:
        rolling = Area.objects.get(code="PROD-ROL")
    areas_dict['rolling'] = rolling
    
    if not Area.objects.filter(code="PROD-FIN").exists():
        finishing = Area.objects.create(
            code="PROD-FIN",
            name="Finishing Area",
            description="Area for final processing and quality control",
            parent=production
        )
    else:
        finishing = Area.objects.get(code="PROD-FIN")
    areas_dict['finishing'] = finishing
    
    # Warehouse sub-areas
    if not Area.objects.filter(code="WH-RAW").exists():
        raw_storage = Area.objects.create(
            code="WH-RAW",
            name="Raw Materials Storage",
            description="Storage area for raw materials",
            parent=warehouse
        )
    else:
        raw_storage = Area.objects.get(code="WH-RAW")
    areas_dict['raw_storage'] = raw_storage
    
    if not Area.objects.filter(code="WH-FIN").exists():
        finished_storage = Area.objects.create(
            code="WH-FIN",
            name="Finished Goods Storage",
            description="Storage area for finished products",
            parent=warehouse
        )
    else:
        finished_storage = Area.objects.get(code="WH-FIN")
    areas_dict['finished_storage'] = finished_storage
    
    # Maintenance sub-areas
    if not Area.objects.filter(code="MAINT-WS").exists():
        workshop = Area.objects.create(
            code="MAINT-WS",
            name="Maintenance Workshop",
            description="Workshop for equipment repairs",
            parent=maintenance_area
        )
    else:
        workshop = Area.objects.get(code="MAINT-WS")
    areas_dict['workshop'] = workshop
    
    if not Area.objects.filter(code="MAINT-TR").exists():
        tool_room = Area.objects.create(
            code="MAINT-TR",
            name="Tool Room",
            description="Storage and maintenance of tools",
            parent=maintenance_area
        )
    else:
        tool_room = Area.objects.get(code="MAINT-TR")
    areas_dict['tool_room'] = tool_room
    
    print(f"Area count: {Area.objects.count()} areas and sub-areas")
    return areas_dict

# Create equipment
def create_equipment(areas):
    equipment_dict = {}
    
    # Melting area equipment
    if not Equipment.objects.filter(code="EQ-MLT-001").exists():
        furnace = Equipment.objects.create(
            code="EQ-MLT-001",
            name="Electric Arc Furnace",
            equipment_type="machine",
            status="operational",
            manufacturer="Steel Tech Inc.",
            model="EAF-5000",
            serial_number="ST78945612",
            area=areas['melting'],
            installation_date=timezone.make_aware(datetime.datetime(2018, 5, 15)),
            description="Main electric arc furnace for melting scrap metal",
        )
    else:
        furnace = Equipment.objects.get(code="EQ-MLT-001")
    equipment_dict['furnace'] = furnace
    
    if not Equipment.objects.filter(code="EQ-MLT-002").exists():
        furnace_control = Equipment.objects.create(
            code="EQ-MLT-002",
            name="Furnace Control System",
            equipment_type="system",
            status="operational",
            manufacturer="Control Systems Ltd.",
            model="CS-800",
            serial_number="CS55623489",
            area=areas['melting'],
            parent=furnace,
            installation_date=timezone.make_aware(datetime.datetime(2018, 5, 15)),
            description="Control system for the electric arc furnace",
        )
    else:
        furnace_control = Equipment.objects.get(code="EQ-MLT-002")
    equipment_dict['furnace_control'] = furnace_control
    
    if not Equipment.objects.filter(code="EQ-MLT-003").exists():
        charging_crane = Equipment.objects.create(
            code="EQ-MLT-003",
            name="Charging Crane",
            equipment_type="machine",
            status="maintenance",
            manufacturer="Heavy Lift Co.",
            model="HC-2000",
            serial_number="HC23456789",
            area=areas['melting'],
            installation_date=timezone.make_aware(datetime.datetime(2018, 6, 10)),
            description="Overhead crane for charging the furnace with raw materials",
        )
    else:
        charging_crane = Equipment.objects.get(code="EQ-MLT-003")
    equipment_dict['charging_crane'] = charging_crane
    
    # Casting area equipment
    if not Equipment.objects.filter(code="EQ-CST-001").exists():
        continuous_caster = Equipment.objects.create(
            code="EQ-CST-001",
            name="Continuous Casting Machine",
            equipment_type="machine",
            status="operational",
            manufacturer="Steel Formers Inc.",
            model="CCM-800",
            serial_number="SF45678901",
            area=areas['casting'],
            installation_date=timezone.make_aware(datetime.datetime(2019, 3, 22)),
            description="Continuous casting machine for slab production",
        )
    else:
        continuous_caster = Equipment.objects.get(code="EQ-CST-001")
    equipment_dict['continuous_caster'] = continuous_caster
    
    if not Equipment.objects.filter(code="EQ-CST-002").exists():
        ladle_turret = Equipment.objects.create(
            code="EQ-CST-002",
            name="Ladle Turret",
            equipment_type="machine",
            status="operational",
            manufacturer="Steel Formers Inc.",
            model="LT-400",
            serial_number="SF45678902",
            area=areas['casting'],
            installation_date=timezone.make_aware(datetime.datetime(2019, 3, 25)),
            description="Rotating turret for ladle positioning",
        )
    else:
        ladle_turret = Equipment.objects.get(code="EQ-CST-002")
    equipment_dict['ladle_turret'] = ladle_turret
    
    # Rolling mill equipment
    if not Equipment.objects.filter(code="EQ-ROL-001").exists():
        roughing_mill = Equipment.objects.create(
            code="EQ-ROL-001",
            name="Roughing Mill",
            equipment_type="machine",
            status="operational",
            manufacturer="Rolling Tech Ltd.",
            model="RM-1000",
            serial_number="RT34567890",
            area=areas['rolling'],
            installation_date=timezone.make_aware(datetime.datetime(2017, 8, 15)),
            description="Primary rolling mill for initial reduction",
        )
    else:
        roughing_mill = Equipment.objects.get(code="EQ-ROL-001")
    equipment_dict['roughing_mill'] = roughing_mill
    
    if not Equipment.objects.filter(code="EQ-ROL-002").exists():
        finishing_mill = Equipment.objects.create(
            code="EQ-ROL-002",
            name="Finishing Mill",
            equipment_type="machine",
            status="out_of_service",
            manufacturer="Rolling Tech Ltd.",
            model="FM-800",
            serial_number="RT34567891",
            area=areas['rolling'],
            installation_date=timezone.make_aware(datetime.datetime(2017, 9, 5)),
            description="Finishing mill for final dimension control",
        )
    else:
        finishing_mill = Equipment.objects.get(code="EQ-ROL-002")
    equipment_dict['finishing_mill'] = finishing_mill
    
    # Finishing area equipment
    if not Equipment.objects.filter(code="EQ-FIN-001").exists():
        cooling_bed = Equipment.objects.create(
            code="EQ-FIN-001",
            name="Cooling Bed",
            equipment_type="machine",
            status="operational",
            manufacturer="Steel Processors Inc.",
            model="CB-500",
            serial_number="SP12345678",
            area=areas['finishing'],
            installation_date=timezone.make_aware(datetime.datetime(2018, 2, 10)),
            description="Cooling bed for controlled cooling of rolled products",
        )
    else:
        cooling_bed = Equipment.objects.get(code="EQ-FIN-001")
    equipment_dict['cooling_bed'] = cooling_bed
    
    if not Equipment.objects.filter(code="EQ-FIN-002").exists():
        shearing_machine = Equipment.objects.create(
            code="EQ-FIN-002",
            name="Shearing Machine",
            equipment_type="machine",
            status="maintenance",
            manufacturer="Cut Master GmbH",
            model="SM-2000",
            serial_number="CM87654321",
            area=areas['finishing'],
            installation_date=timezone.make_aware(datetime.datetime(2018, 3, 15)),
            description="Precision shearing machine for cutting to length",
        )
    else:
        shearing_machine = Equipment.objects.get(code="EQ-FIN-002")
    equipment_dict['shearing_machine'] = shearing_machine
    
    # Warehouse equipment
    if not Equipment.objects.filter(code="EQ-WH-001").exists():
        overhead_crane = Equipment.objects.create(
            code="EQ-WH-001",
            name="Overhead Crane",
            equipment_type="machine",
            status="operational",
            manufacturer="Heavy Lift Co.",
            model="OC-5000",
            serial_number="HC12345678",
            area=areas['warehouse'],
            installation_date=timezone.make_aware(datetime.datetime(2019, 5, 20)),
            description="Main overhead crane for warehouse operations",
        )
    else:
        overhead_crane = Equipment.objects.get(code="EQ-WH-001")
    equipment_dict['overhead_crane'] = overhead_crane
    
    if not Equipment.objects.filter(code="EQ-WH-002").exists():
        forklift = Equipment.objects.create(
            code="EQ-WH-002",
            name="Forklift",
            equipment_type="machine",
            status="operational",
            manufacturer="Industrial Movers Ltd.",
            model="FL-200",
            serial_number="IM98765432",
            area=areas['raw_storage'],
            installation_date=timezone.make_aware(datetime.datetime(2020, 1, 15)),
            description="Electric forklift for material handling",
        )
    else:
        forklift = Equipment.objects.get(code="EQ-WH-002")
    equipment_dict['forklift'] = forklift
    
    # Workshop equipment
    if not Equipment.objects.filter(code="EQ-WS-001").exists():
        lathe = Equipment.objects.create(
            code="EQ-WS-001",
            name="CNC Lathe",
            equipment_type="machine",
            status="operational",
            manufacturer="Precision Tools Inc.",
            model="CNC-L500",
            serial_number="PT24681357",
            area=areas['workshop'],
            installation_date=timezone.make_aware(datetime.datetime(2019, 8, 10)),
            description="Computer numerical control lathe for parts manufacturing",
        )
    else:
        lathe = Equipment.objects.get(code="EQ-WS-001")
    equipment_dict['lathe'] = lathe
    
    if not Equipment.objects.filter(code="EQ-WS-002").exists():
        milling_machine = Equipment.objects.create(
            code="EQ-WS-002",
            name="Milling Machine",
            equipment_type="machine",
            status="operational",
            manufacturer="Precision Tools Inc.",
            model="MM-300",
            serial_number="PT13579246",
            area=areas['workshop'],
            installation_date=timezone.make_aware(datetime.datetime(2019, 9, 5)),
            description="Vertical milling machine for parts manufacturing",
        )
    else:
        milling_machine = Equipment.objects.get(code="EQ-WS-002")
    equipment_dict['milling_machine'] = milling_machine
    
    print(f"Equipment count: {Equipment.objects.count()} equipment items")
    
    return equipment_dict

# Create maintenance logs and tasks
def create_maintenance(equipment_dict, technicians_dict):
    # Check if we've already created maintenance logs
    if MaintenanceLog.objects.filter(title="Annual Furnace Inspection").exists():
        print("Maintenance logs already exist, skipping creation...")
        return
    
    # Create maintenance logs
    logs = []
    
    # Preventive maintenance logs
    log1 = MaintenanceLog.objects.create(
        equipment=equipment_dict['furnace'],
        date=timezone.make_aware(datetime.datetime(2023, 2, 15)),
        title="Annual Furnace Inspection",
        maintenance_type="preventive",
        duration=8,
        observations="Refractory lining shows signs of wear but still within acceptable limits. Electrode holders need replacement within next 3 months.",
        maintenance_result="successful",
        description="Annual inspection of electric arc furnace including refractory lining check, electrode system inspection, and hydraulic system maintenance.",
        created_by=admin_user
    )
    # Add technicians
    log1.technicians.add(technicians_dict['jsmith'], technicians_dict['mjohnson'])
    logs.append(log1)
    
    log2 = MaintenanceLog.objects.create(
        equipment=equipment_dict['continuous_caster'],
        date=timezone.make_aware(datetime.datetime(2023, 3, 10)),
        title="Quarterly Caster Maintenance",
        maintenance_type="preventive",
        duration=6,
        observations="Mold copper plates showing normal wear. Cooling water filters replaced. All systems operating within parameters.",
        maintenance_result="successful",
        description="Quarterly maintenance of continuous casting machine including mold inspection, cooling system check, and roller alignment.",
        created_by=admin_user
    )
    log2.technicians.add(technicians_dict['rbrown'], technicians_dict['dlee'])
    logs.append(log2)
    
    # Corrective maintenance logs
    log3 = MaintenanceLog.objects.create(
        equipment=equipment_dict['charging_crane'],
        date=timezone.make_aware(datetime.datetime(2023, 4, 5)),
        title="Crane Motor Replacement",
        maintenance_type="corrective",
        duration=12,
        observations="Motor replaced successfully. Old motor sent for analysis. Possible causes include overloading and inadequate lubrication.",
        maintenance_result="successful",
        description="Replacement of main hoist motor due to bearing failure.",
        created_by=admin_user
    )
    log3.technicians.add(technicians_dict['mjohnson'], technicians_dict['swilliams'])
    logs.append(log3)
    
    log4 = MaintenanceLog.objects.create(
        equipment=equipment_dict['finishing_mill'],
        date=timezone.make_aware(datetime.datetime(2023, 4, 20)),
        title="Mill Drive Failure",
        maintenance_type="corrective",
        duration=24,
        observations="Main drive gearbox suffered severe damage. Temporary repairs made but complete rebuilding required. Parts ordered from manufacturer.",
        maintenance_result="partial",
        description="Emergency repair of main drive system following catastrophic failure during operation.",
        created_by=admin_user
    )
    log4.technicians.add(technicians_dict['rbrown'], technicians_dict['dlee'], technicians_dict['jsmith'])
    logs.append(log4)
    
    log5 = MaintenanceLog.objects.create(
        equipment=equipment_dict['shearing_machine'],
        date=timezone.make_aware(datetime.datetime(2023, 5, 12)),
        title="Hydraulic System Leak",
        maintenance_type="corrective",
        duration=4,
        observations="Leak located at main pressure line fitting. Fitting replaced and system pressure tested.",
        maintenance_result="successful",
        description="Repair of hydraulic system leak on shearing machine.",
        created_by=admin_user
    )
    log5.technicians.add(technicians_dict['swilliams'], technicians_dict['aturner'])
    logs.append(log5)
    
    # Predictive maintenance logs
    log6 = MaintenanceLog.objects.create(
        equipment=equipment_dict['roughing_mill'],
        date=timezone.make_aware(datetime.datetime(2023, 5, 5)),
        title="Vibration Analysis",
        maintenance_type="predictive",
        duration=2,
        observations="Vibration levels within normal parameters. No significant changes from baseline measurements.",
        maintenance_result="successful",
        description="Scheduled vibration analysis of roughing mill drive train.",
        created_by=admin_user
    )
    log6.technicians.add(technicians_dict['aturner'])
    logs.append(log6)
    
    print(f"Created {len(logs)} maintenance logs")
    
    # Create maintenance tasks
    tasks = []
    
    # Create tasks for each log
    for log in logs:
        # Past completed tasks
        task = MaintenanceTask.objects.create(
            maintenance_log=log,
            description=f"Follow-up inspection for {log.title}",
            due_date=log.date + datetime.timedelta(days=30),
            assigned_to=admin_user,
            status="completed",
            completed_date=log.date + datetime.timedelta(days=30),
            notes="Completed as scheduled. No issues found."
        )
        tasks.append(task)
    
    # Current pending tasks
    today = timezone.now().date()
    
    # Task due today
    tasks.append(MaintenanceTask.objects.create(
        maintenance_log=logs[0],  # Furnace inspection
        description="Replace electrode holders on electric arc furnace",
        due_date=today,
        assigned_to=admin_user,
        status="pending"
    ))
    
    # Task due in near future
    tasks.append(MaintenanceTask.objects.create(
        maintenance_log=logs[1],  # Caster maintenance
        description="Clean and inspect mold cooling channels",
        due_date=today + datetime.timedelta(days=5),
        assigned_to=admin_user,
        status="pending"
    ))
    
    # Overdue task
    tasks.append(MaintenanceTask.objects.create(
        maintenance_log=logs[3],  # Mill drive failure
        description="Complete rebuilding of main drive gearbox",
        due_date=today - datetime.timedelta(days=10),
        assigned_to=admin_user,
        status="in_progress"
    ))
    
    # Task for near future
    tasks.append(MaintenanceTask.objects.create(
        maintenance_log=logs[5],  # Vibration analysis
        description="Perform follow-up vibration analysis on roughing mill",
        due_date=today + datetime.timedelta(days=15),
        assigned_to=admin_user,
        status="pending"
    ))
    
    print(f"Created {len(tasks)} maintenance tasks")

# Create technical specifications
def create_specifications(equipment_dict):
    # Check if we've already created specs
    if TechnicalSpecification.objects.filter(equipment=equipment_dict['furnace']).exists():
        print("Technical specifications already exist, skipping creation...")
        return
    
    specs_count = 0
    # Furnace specifications
    furnace_specs = [
        {"specification": "Capacity", "value": "50", "unit": "tonnes"},
        {"specification": "Power Rating", "value": "25", "unit": "MW"},
        {"specification": "Electrode Diameter", "value": "600", "unit": "mm"},
        {"specification": "Transformer Rating", "value": "30", "unit": "MVA"},
        {"specification": "Tapping Temperature", "value": "1650", "unit": "°C"}
    ]
    
    for spec in furnace_specs:
        TechnicalSpecification.objects.create(
            equipment=equipment_dict['furnace'],
            **spec
        )
        specs_count += 1
    
    # Continuous caster specifications
    caster_specs = [
        {"specification": "Casting Speed", "value": "1.2", "unit": "m/min"},
        {"specification": "Slab Width", "value": "1500", "unit": "mm"},
        {"specification": "Slab Thickness", "value": "250", "unit": "mm"},
        {"specification": "Cooling Rate", "value": "15", "unit": "°C/s"},
        {"specification": "Metallurgical Length", "value": "35", "unit": "m"}
    ]
    
    for spec in caster_specs:
        TechnicalSpecification.objects.create(
            equipment=equipment_dict['continuous_caster'],
            **spec
        )
        specs_count += 1
    
    # Rolling mills specifications
    roughing_mill_specs = [
        {"specification": "Roll Diameter", "value": "900", "unit": "mm"},
        {"specification": "Motor Power", "value": "2000", "unit": "kW"},
        {"specification": "Maximum Reduction", "value": "40", "unit": "%"},
        {"specification": "Maximum Width", "value": "1800", "unit": "mm"},
        {"specification": "Roll Speed", "value": "300", "unit": "rpm"}
    ]
    
    for spec in roughing_mill_specs:
        TechnicalSpecification.objects.create(
            equipment=equipment_dict['roughing_mill'],
            **spec
        )
        specs_count += 1
    
    finishing_mill_specs = [
        {"specification": "Roll Diameter", "value": "600", "unit": "mm"},
        {"specification": "Motor Power", "value": "1500", "unit": "kW"},
        {"specification": "Maximum Reduction", "value": "25", "unit": "%"},
        {"specification": "Maximum Width", "value": "1600", "unit": "mm"},
        {"specification": "Roll Speed", "value": "500", "unit": "rpm"}
    ]
    
    for spec in finishing_mill_specs:
        TechnicalSpecification.objects.create(
            equipment=equipment_dict['finishing_mill'],
            **spec
        )
        specs_count += 1
    
    print(f"Created {specs_count} technical specifications")

# Main execution
if __name__ == '__main__':
    technicians = create_technicians()
    areas = create_areas()
    equipment_dict = create_equipment(areas)
    create_maintenance(equipment_dict, technicians)
    create_specifications(equipment_dict)
    
    print("Dummy data creation complete!") 