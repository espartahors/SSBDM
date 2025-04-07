#!/usr/bin/env python
"""
Script to populate the PostgreSQL database with dummy data using the new model structure
with UUIDs and enhanced relationships.
"""
import os
import sys
import random
import datetime
import uuid
import traceback
from django.db import transaction, connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSBDM.settings')
import django
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User

# Import models
from equipment_new.models import Area, Equipment, TechnicalSpecification
from spare_parts.models import Category, SparePart, SparePartTransaction
from documents.models import DocumentCategory, EquipmentDocument, DOCUMENT_TYPE_CHOICES
from ssbom.models import BOMRelationship, EquipmentSparePartUsage

print("Creating dummy data for SSBDM with PostgreSQL...")
print(f"Using database: {connection.settings_dict['NAME']} on {connection.settings_dict['HOST']}:{connection.settings_dict['PORT']}")

# Verify database connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print(f"Connected to PostgreSQL: {db_version}")
except Exception as e:
    print(f"Error connecting to database: {e}")
    traceback.print_exc()
    sys.exit(1)

# Get or create admin user for assignments
@transaction.atomic
def get_or_create_admin():
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        try:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin'
            )
            print("Created admin user")
        except Exception as e:
            print(f"Error creating admin user: {e}")
            raise
    else:
        print("Using existing admin user")
    return admin_user

# Create technicians
@transaction.atomic
def create_technicians():
    try:
        technicians = []
        usernames = ['jsmith', 'mjohnson', 'rbrown', 'dlee', 'swilliams', 'aturner']
        first_names = ['John', 'Mike', 'Robert', 'David', 'Sarah', 'Alex']
        last_names = ['Smith', 'Johnson', 'Brown', 'Lee', 'Williams', 'Turner']
        
        for i, username in enumerate(usernames):
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username, 
                    f"{first_names[i].lower()}.{last_names[i].lower()}@example.com", 
                    'password',
                    first_name=first_names[i], 
                    last_name=last_names[i]
                )
                technicians.append(user)
            else:
                technicians.append(User.objects.get(username=username))
        
        print(f"Created or retrieved {len(technicians)} technicians")
        return dict(zip(usernames, technicians))
    except Exception as e:
        print(f"Error creating technicians: {e}")
        traceback.print_exc()
        raise

# Create areas and sub-areas
@transaction.atomic
def create_areas():
    try:
        areas_dict = {}
        main_areas = [
            {'code': 'PROD', 'name': 'Production Facility', 'desc': 'Main production area for steel manufacturing'},
            {'code': 'WH', 'name': 'Warehouse', 'desc': 'Storage area for raw materials and finished products'},
            {'code': 'MAINT', 'name': 'Maintenance Department', 'desc': 'Central maintenance and repair facility'},
            {'code': 'OFF', 'name': 'Administrative Offices', 'desc': 'Management and administrative departments'}
        ]
        
        for area_data in main_areas:
            area, created = Area.objects.get_or_create(
                code=area_data['code'],
                defaults={
                    'id': uuid.uuid4(),
                    'name': area_data['name'],
                    'description': area_data['desc'],
                }
            )
            areas_dict[area_data['code'].lower()] = area
            if created:
                print(f"Created area: {area.name}")
        
        # Sub-areas for production
        prod_subareas = [
            {'code': 'PROD-MLT', 'name': 'Melting Area', 'desc': 'Area for melting raw materials', 'parent': 'prod'},
            {'code': 'PROD-CST', 'name': 'Casting Area', 'desc': 'Area for casting molten metal', 'parent': 'prod'},
            {'code': 'PROD-ROL', 'name': 'Rolling Mill', 'desc': 'Area for hot and cold rolling of steel', 'parent': 'prod'},
            {'code': 'PROD-FIN', 'name': 'Finishing Area', 'desc': 'Area for final processing and quality control', 'parent': 'prod'}
        ]
        
        for area_data in prod_subareas:
            area, created = Area.objects.get_or_create(
                code=area_data['code'],
                defaults={
                    'id': uuid.uuid4(),
                    'name': area_data['name'],
                    'description': area_data['desc'],
                    'parent': areas_dict[area_data['parent']],
                }
            )
            areas_dict[area_data['code'].lower().replace('-', '_')] = area
            if created:
                print(f"Created sub-area: {area.name}")
        
        # Sub-areas for warehouse
        wh_subareas = [
            {'code': 'WH-RAW', 'name': 'Raw Materials Storage', 'desc': 'Storage area for raw materials', 'parent': 'wh'},
            {'code': 'WH-FIN', 'name': 'Finished Goods Storage', 'desc': 'Storage area for finished products', 'parent': 'wh'}
        ]
        
        for area_data in wh_subareas:
            area, created = Area.objects.get_or_create(
                code=area_data['code'],
                defaults={
                    'id': uuid.uuid4(),
                    'name': area_data['name'],
                    'description': area_data['desc'],
                    'parent': areas_dict[area_data['parent']],
                }
            )
            areas_dict[area_data['code'].lower().replace('-', '_')] = area
            if created:
                print(f"Created sub-area: {area.name}")
        
        # Sub-areas for maintenance
        maint_subareas = [
            {'code': 'MAINT-WS', 'name': 'Maintenance Workshop', 'desc': 'Workshop for equipment repairs', 'parent': 'maint'},
            {'code': 'MAINT-TR', 'name': 'Tool Room', 'desc': 'Storage and maintenance of tools', 'parent': 'maint'}
        ]
        
        for area_data in maint_subareas:
            area, created = Area.objects.get_or_create(
                code=area_data['code'],
                defaults={
                    'id': uuid.uuid4(),
                    'name': area_data['name'],
                    'description': area_data['desc'],
                    'parent': areas_dict[area_data['parent']],
                }
            )
            areas_dict[area_data['code'].lower().replace('-', '_')] = area
            if created:
                print(f"Created sub-area: {area.name}")
        
        area_count = Area.objects.count()
        print(f"Area count: {area_count} areas and sub-areas")
        
        if area_count == 0:
            print("WARNING: No areas were created!")
            
        return areas_dict
    except Exception as e:
        print(f"Error creating areas: {e}")
        traceback.print_exc()
        raise

# Create equipment with stricter error checking
@transaction.atomic
def create_equipment(areas, admin_user):
    try:
        equipment_dict = {}
        
        # Melting equipment
        melting_equipment = [
            {
                'code': 'EQ-MLT-001',
                'name': 'Electric Arc Furnace',
                'type': 'machine',
                'area': 'prod_mlt',
                'manufacturer': 'Steel Tech Inc.',
                'model': 'EAF-5000',
                'sn': 'ST78945612',
                'year': 2018,
                'month': 5,
                'day': 15,
                'desc': 'Main electric arc furnace for melting scrap metal',
                'is_critical': True,
                'cost': 2500000.00
            },
            {
                'code': 'EQ-MLT-002',
                'name': 'Furnace Control System',
                'type': 'system',
                'area': 'prod_mlt',
                'parent': 'EQ-MLT-001',
                'manufacturer': 'Control Systems Ltd.',
                'model': 'CS-800',
                'sn': 'CS55623489',
                'year': 2018,
                'month': 5,
                'day': 15,
                'desc': 'Control system for the electric arc furnace',
                'is_critical': True,
                'cost': 450000.00
            }
        ]
        
        # Check if we have the required areas
        required_areas = ['prod_mlt', 'prod_cst']
        for area_key in required_areas:
            if area_key not in areas:
                print(f"ERROR: Required area {area_key} not found in area dictionary")
                print(f"Available areas: {list(areas.keys())}")
                raise ValueError(f"Required area {area_key} not found")
        
        # Create melting equipment
        for eq_data in melting_equipment:
            parent = None
            if 'parent' in eq_data and eq_data['parent'] in equipment_dict:
                parent = equipment_dict[eq_data['parent']]
                
            equipment, created = Equipment.objects.get_or_create(
                code=eq_data['code'],
                defaults={
                    'id': uuid.uuid4(),
                    'name': eq_data['name'],
                    'equipment_type': eq_data['type'],
                    'area': areas[eq_data['area']],
                    'parent': parent,
                    'manufacturer': eq_data['manufacturer'],
                    'model': eq_data['model'],
                    'serial_number': eq_data['sn'],
                    'installation_date': timezone.make_aware(datetime.datetime(eq_data['year'], eq_data['month'], eq_data['day'])),
                    'status': 'operational',
                    'description': eq_data['desc'],
                    'is_critical': eq_data.get('is_critical', False),
                    'purchase_cost': eq_data.get('cost'),
                    'purchase_date': timezone.make_aware(datetime.datetime(eq_data['year'], eq_data['month'], 1)),
                    'created_by': admin_user,
                    'updated_by': admin_user
                }
            )
            equipment_dict[eq_data['code']] = equipment
            if created:
                print(f"Created equipment: {equipment.name}")
            
        # Casting equipment
        casting_equipment = [
            {
                'code': 'EQ-CST-001',
                'name': 'Continuous Casting Machine',
                'type': 'machine',
                'area': 'prod_cst',
                'manufacturer': 'MetalCast Ltd.',
                'model': 'MC-2000',
                'sn': 'MCL12378945',
                'year': 2019,
                'month': 3,
                'day': 10,
                'desc': 'Continuous casting machine for steel billets',
                'is_critical': True,
                'cost': 1800000.00
            },
            {
                'code': 'EQ-CST-002',
                'name': 'Ladle Turret',
                'type': 'machine',
                'area': 'prod_cst',
                'manufacturer': 'MetalCast Ltd.',
                'model': 'LT-500',
                'sn': 'LT56781234',
                'year': 2019,
                'month': 3,
                'day': 12,
                'desc': 'Ladle turret for continuous casting',
                'is_critical': True,
                'cost': 650000.00
            }
        ]
        
        # Create casting equipment
        for eq_data in casting_equipment:
            parent = None
            if 'parent' in eq_data and eq_data['parent'] in equipment_dict:
                parent = equipment_dict[eq_data['parent']]
                
            equipment, created = Equipment.objects.get_or_create(
                code=eq_data['code'],
                defaults={
                    'id': uuid.uuid4(),
                    'name': eq_data['name'],
                    'equipment_type': eq_data['type'],
                    'area': areas[eq_data['area']],
                    'parent': parent,
                    'manufacturer': eq_data['manufacturer'],
                    'model': eq_data['model'],
                    'serial_number': eq_data['sn'],
                    'installation_date': timezone.make_aware(datetime.datetime(eq_data['year'], eq_data['month'], eq_data['day'])),
                    'status': 'operational',
                    'description': eq_data['desc'],
                    'is_critical': eq_data.get('is_critical', False),
                    'purchase_cost': eq_data.get('cost'),
                    'purchase_date': timezone.make_aware(datetime.datetime(eq_data['year'], eq_data['month'], 1)),
                    'created_by': admin_user,
                    'updated_by': admin_user
                }
            )
            equipment_dict[eq_data['code']] = equipment
            if created:
                print(f"Created equipment: {equipment.name}")
        
        equipment_count = Equipment.objects.count()
        print(f"Equipment count: {equipment_count} items")
        
        if equipment_count == 0:
            print("WARNING: No equipment was created!")
        
        return equipment_dict
    except Exception as e:
        print(f"Error creating equipment: {e}")
        traceback.print_exc()
        raise

# Create technical specifications
def create_specifications(equipment_dict, admin_user):
    # Clear existing specifications
    # TechnicalSpecification.objects.all().delete()
    
    # Common specifications for equipment
    spec_templates = {
        'EQ-MLT-001': [  # Electric Arc Furnace
            {'name': 'Power Rating', 'value': '25000', 'unit': 'kW'},
            {'name': 'Capacity', 'value': '100', 'unit': 'tons'},
            {'name': 'Electrode Diameter', 'value': '750', 'unit': 'mm'},
            {'name': 'Maximum Temperature', 'value': '1800', 'unit': '°C'},
            {'name': 'Cooling System', 'value': 'Water-cooled', 'unit': ''},
        ],
        'EQ-MLT-002': [  # Furnace Control System
            {'name': 'Power Supply', 'value': '240', 'unit': 'V'},
            {'name': 'Control Interface', 'value': 'Touch Screen HMI', 'unit': ''},
            {'name': 'Communication Protocol', 'value': 'Modbus TCP/IP', 'unit': ''},
            {'name': 'Software Version', 'value': '5.2.3', 'unit': ''},
        ],
        'EQ-CST-001': [  # Continuous Casting Machine
            {'name': 'Casting Speed', 'value': '2.5', 'unit': 'm/min'},
            {'name': 'Strand Count', 'value': '4', 'unit': ''},
            {'name': 'Billet Size', 'value': '150x150', 'unit': 'mm'},
            {'name': 'Cooling Rate', 'value': '15', 'unit': '°C/s'},
            {'name': 'Machine Length', 'value': '25', 'unit': 'm'},
        ],
        'EQ-CST-002': [  # Ladle Turret
            {'name': 'Ladle Capacity', 'value': '100', 'unit': 'tons'},
            {'name': 'Rotation Speed', 'value': '0.5', 'unit': 'rpm'},
            {'name': 'Drive Power', 'value': '75', 'unit': 'kW'},
            {'name': 'Maximum Load', 'value': '120', 'unit': 'tons'},
        ],
    }
    
    spec_count = 0
    for eq_code, specs in spec_templates.items():
        equipment = equipment_dict.get(eq_code)
        if not equipment:
            continue
            
        for spec in specs:
            # Check if spec already exists
            if not TechnicalSpecification.objects.filter(equipment=equipment, specification=spec['name']).exists():
                TechnicalSpecification.objects.create(
                    id=uuid.uuid4(),
                    equipment=equipment,
                    specification=spec['name'],
                    value=spec['value'],
                    unit=spec['unit'],
                    created_by=admin_user,
                    updated_by=admin_user
                )
                spec_count += 1
    
    print(f"Created {spec_count} technical specifications")

# Create spare part categories
def create_spare_part_categories(admin_user):
    categories_dict = {}
    
    # Main categories
    main_categories = [
        {'code': 'ELEC', 'name': 'Electrical Parts'},
        {'code': 'MECH', 'name': 'Mechanical Parts'},
        {'code': 'HYD', 'name': 'Hydraulic Parts'},
        {'code': 'PNEU', 'name': 'Pneumatic Parts'},
    ]
    
    # Create main categories
    for cat_data in main_categories:
        category, created = Category.objects.get_or_create(
            code=cat_data['code'],
            defaults={
                'id': uuid.uuid4(),
                'name': cat_data['name'],
                'description': f"Main category for {cat_data['name']}",
                'created_by': admin_user
            }
        )
        categories_dict[cat_data['code'].lower()] = category
    
    # Electrical subcategories
    elec_subcategories = [
        {'code': 'ELEC-MOT', 'name': 'Electric Motors', 'parent': 'elec'},
        {'code': 'ELEC-SEN', 'name': 'Sensors', 'parent': 'elec'},
        {'code': 'ELEC-CON', 'name': 'Controllers', 'parent': 'elec'},
    ]
    
    for cat_data in elec_subcategories:
        category, created = Category.objects.get_or_create(
            code=cat_data['code'],
            defaults={
                'id': uuid.uuid4(),
                'name': cat_data['name'],
                'parent': categories_dict[cat_data['parent']],
                'description': f"Subcategory for {cat_data['name']}",
                'created_by': admin_user
            }
        )
        categories_dict[cat_data['code'].lower().replace('-', '_')] = category
    
    # Mechanical subcategories
    mech_subcategories = [
        {'code': 'MECH-BRG', 'name': 'Bearings', 'parent': 'mech'},
        {'code': 'MECH-GEA', 'name': 'Gears', 'parent': 'mech'},
        {'code': 'MECH-FAS', 'name': 'Fasteners', 'parent': 'mech'},
    ]
    
    for cat_data in mech_subcategories:
        category, created = Category.objects.get_or_create(
            code=cat_data['code'],
            defaults={
                'id': uuid.uuid4(),
                'name': cat_data['name'],
                'parent': categories_dict[cat_data['parent']],
                'description': f"Subcategory for {cat_data['name']}",
                'created_by': admin_user
            }
        )
        categories_dict[cat_data['code'].lower().replace('-', '_')] = category
        
    # Hydraulic subcategories
    hyd_subcategories = [
        {'code': 'HYD-PMP', 'name': 'Hydraulic Pumps', 'parent': 'hyd'},
        {'code': 'HYD-CYL', 'name': 'Hydraulic Cylinders', 'parent': 'hyd'},
    ]
    
    for cat_data in hyd_subcategories:
        category, created = Category.objects.get_or_create(
            code=cat_data['code'],
            defaults={
                'id': uuid.uuid4(),
                'name': cat_data['name'],
                'parent': categories_dict[cat_data['parent']],
                'description': f"Subcategory for {cat_data['name']}",
                'created_by': admin_user
            }
        )
        categories_dict[cat_data['code'].lower().replace('-', '_')] = category
    
    # Pneumatic subcategories
    pneu_subcategories = [
        {'code': 'PNEU-VLV', 'name': 'Pneumatic Valves', 'parent': 'pneu'},
        {'code': 'PNEU-CYL', 'name': 'Pneumatic Cylinders', 'parent': 'pneu'},
    ]
    
    for cat_data in pneu_subcategories:
        category, created = Category.objects.get_or_create(
            code=cat_data['code'],
            defaults={
                'id': uuid.uuid4(),
                'name': cat_data['name'],
                'parent': categories_dict[cat_data['parent']],
                'description': f"Subcategory for {cat_data['name']}",
                'created_by': admin_user
            }
        )
        categories_dict[cat_data['code'].lower().replace('-', '_')] = category
    
    print(f"Category count: {Category.objects.count()} categories and subcategories")
    return categories_dict

# Create spare parts
def create_spare_parts(categories_dict, admin_user):
    parts_dict = {}
    
    # Sample spare parts
    parts_data = [
        {
            'code': 'MTR-001',
            'name': 'Electric Motor 5HP',
            'category': categories_dict['elec_mot'],
            'price': 450.00,
            'minimum_stock': 2,
            'current_stock': 3,
            'unit': 'pcs',
            'location': 'Warehouse A-12',
            'manufacturer': 'Siemens',
            'supplier': 'ElectroMotors Inc.',
            'supplier_reference': 'EM5HP-120',
            'lead_time': 14,
            'description': 'Three-phase electric motor, 5HP, 415V, 1450rpm'
        },
        {
            'code': 'BRG-001',
            'name': 'Bearing Assembly 60mm',
            'category': categories_dict['mech_brg'],
            'price': 85.50,
            'minimum_stock': 5,
            'current_stock': 8,
            'unit': 'pcs',
            'location': 'Warehouse B-05',
            'manufacturer': 'SKF',
            'supplier': 'Bearing Solutions Ltd.',
            'supplier_reference': 'BA60-ST',
            'lead_time': 7,
            'description': 'Double-row spherical roller bearing, 60mm bore'
        },
        {
            'code': 'PMP-001',
            'name': 'Hydraulic Pump 1500PSI',
            'category': categories_dict['hyd_pmp'],
            'price': 750.00,
            'minimum_stock': 1,
            'current_stock': 2,
            'unit': 'pcs',
            'location': 'Warehouse C-03',
            'manufacturer': 'Parker Hannifin',
            'supplier': 'HydroTech Systems',
            'supplier_reference': 'HP1500-A',
            'lead_time': 21,
            'description': 'Variable displacement hydraulic pump, max 1500 PSI'
        },
        {
            'code': 'VLV-001',
            'name': 'Pneumatic Control Valve',
            'category': categories_dict['pneu_vlv'],
            'price': 120.75,
            'minimum_stock': 3,
            'current_stock': 5,
            'unit': 'pcs',
            'location': 'Warehouse B-12',
            'manufacturer': 'Festo',
            'supplier': 'ValveTech Industries',
            'supplier_reference': 'PCV-200',
            'lead_time': 10,
            'description': '5/2-way directional control valve for pneumatic systems'
        },
        {
            'code': 'SNS-001',
            'name': 'Temperature Sensor 0-600°C',
            'category': categories_dict['elec_sen'],
            'price': 65.25,
            'minimum_stock': 4,
            'current_stock': 6,
            'unit': 'pcs',
            'location': 'Warehouse A-08',
            'manufacturer': 'Endress+Hauser',
            'supplier': 'SensorTech Solutions',
            'supplier_reference': 'TS600-PT100',
            'lead_time': 5,
            'description': 'PT100 temperature sensor, range 0-600°C, 4-20mA output'
        },
        {
            'code': 'BLT-001',
            'name': 'High Strength Bolt Set M12',
            'category': categories_dict['mech_fas'],
            'price': 25.50,
            'minimum_stock': 20,
            'current_stock': 35,
            'unit': 'pack',
            'location': 'Warehouse D-02',
            'manufacturer': 'Fastenal',
            'supplier': 'Fastener Supply Co.',
            'supplier_reference': 'HSB-M12-50',
            'lead_time': 3,
            'description': 'Set of 10 high-strength M12x50mm bolts, class 8.8'
        }
    ]
    
    for part_data in parts_data:
        # Create or get spare part
        part, created = SparePart.objects.get_or_create(
            code=part_data['code'],
            defaults={
                'id': uuid.uuid4(),
                'name': part_data['name'],
                'category': part_data['category'],
                'description': part_data['description'],
                'price': part_data['price'],
                'minimum_stock': part_data['minimum_stock'],
                'current_stock': part_data['current_stock'],
                'unit': part_data['unit'],
                'location': part_data['location'],
                'manufacturer': part_data['manufacturer'],
                'supplier': part_data['supplier'],
                'supplier_reference': part_data['supplier_reference'],
                'lead_time': part_data['lead_time'],
                'notes': f"Sample spare part - {part_data['name']}",
                'created_by': admin_user
            }
        )
        
        parts_dict[part_data['code']] = part
    
    print(f"Spare part count: {len(parts_dict)} parts")
    return parts_dict

# Create spare part transactions
def create_spare_part_transactions(parts_dict, equipment_dict, technicians_dict):
    # Recent transactions
    recent_dates = [
        timezone.now() - datetime.timedelta(days=i) for i in range(1, 31)
    ]
    
    transaction_types = ['received', 'issued', 'returned', 'adjusted']
    transaction_count = 0
    
    for part_code, part in parts_dict.items():
        # Create between 2-5 transactions for each part
        num_transactions = random.randint(2, 5)
        
        for i in range(num_transactions):
            transaction_type = random.choice(transaction_types)
            date = random.choice(recent_dates)
            
            # Determine quantity based on transaction type
            if transaction_type == 'received':
                quantity = random.randint(5, 20)
            elif transaction_type == 'issued':
                quantity = random.randint(1, 3)
            elif transaction_type == 'returned':
                quantity = random.randint(1, 2)
            else:  # adjusted
                quantity = random.randint(1, 5)  # Changed from (-3, 3) to (1, 5) to avoid negative values
                
            # Random equipment for issued items
            equipment = None
            if transaction_type == 'issued':
                equipment = random.choice(list(equipment_dict.values()))
                
            # Random technician
            technician = random.choice(list(technicians_dict.values()))
            
            # Create transaction
            SparePartTransaction.objects.create(
                id=uuid.uuid4(),
                spare_part=part,
                transaction_type=transaction_type,
                quantity=quantity,
                date=date,
                unit_price=part.price if transaction_type == 'received' else None,
                equipment=equipment,
                reference=f"REF-{date.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                notes=f"Sample {transaction_type} transaction",
                created_by=technician
            )
            transaction_count += 1
    
    print(f"Created {transaction_count} spare part transactions")

# Create document categories
def create_document_categories(admin_user):
    doc_categories_dict = {}
    
    # Main categories
    main_categories = [
        {'name': 'Technical Documentation', 'code': 'TECH-DOC', 'description': 'Technical specifications and documentation'},
        {'name': 'Operational Documents', 'code': 'OPS-DOC', 'description': 'Documents related to equipment operation'},
        {'name': 'Maintenance Records', 'code': 'MAINT-DOC', 'description': 'Maintenance procedures and history'},
        {'name': 'Certificates', 'code': 'CERT-DOC', 'description': 'Certification and compliance documents'},
    ]
    
    # Create main categories
    for cat_data in main_categories:
        category, created = DocumentCategory.objects.get_or_create(
            code=cat_data['code'],
            defaults={
                'id': uuid.uuid4(),
                'name': cat_data['name'],
                'description': cat_data['description'],
                'created_by': admin_user
            }
        )
        doc_categories_dict[cat_data['code']] = category
    
    print(f"Document category count: {len(doc_categories_dict)} categories")
    return doc_categories_dict

# Create equipment documents
def create_documents(equipment_dict, doc_categories_dict, admin_user):
    documents_dict = {}
    
    # Generate some documents for each equipment
    for equip_code, equipment in equipment_dict.items():
        # Create 1-3 documents per equipment
        num_docs = random.randint(1, 3)
        
        for i in range(num_docs):
            # Choose random document type
            doc_type = random.choice([choice[0] for choice in DOCUMENT_TYPE_CHOICES])
            
            # Choose random category
            category = random.choice(list(doc_categories_dict.values()))
            
            # Create document
            doc = EquipmentDocument.objects.create(
                id=uuid.uuid4(),
                equipment=equipment,
                title=f"{equipment.name} - {dict(DOCUMENT_TYPE_CHOICES)[doc_type]}",
                document_type=doc_type,
                category=category,
                description=f"Sample document for {equipment.name}",
                document_number=f"DOC-{equip_code}-{i+1}",
                revision="Rev 1.0",
                issue_date=timezone.now() - datetime.timedelta(days=random.randint(30, 365)),
                is_confidential=random.choice([True, False]),
                notes=f"This is a sample document for {equipment.name}",
                uploaded_by=admin_user,
                is_active=True
            )
            
            doc_key = f"{equip_code}_doc_{i+1}"
            documents_dict[doc_key] = doc
    
    print(f"Document count: {len(documents_dict)} documents")
    return documents_dict

# Create relationships between equipment, spare parts, and documents
def create_relationships(equipment_dict, parts_dict, documents_dict, admin_user):
    relationship_count = 0
    
    # Create equipment-spare part relationships
    for equip_code, equipment in equipment_dict.items():
        # Associate 2-4 random parts with each equipment
        num_parts = random.randint(2, 4)
        part_keys = random.sample(list(parts_dict.keys()), min(num_parts, len(parts_dict)))
        
        for part_key in part_keys:
            part = parts_dict[part_key]
            
            # Check if relationship already exists
            if not BOMRelationship.objects.filter(
                equipment=equipment,
                spare_part=part,
                relationship_type='component'
            ).exists():
                # Create relationship
                relationship = BOMRelationship.objects.create(
                    id=uuid.uuid4(),
                    equipment=equipment,
                    spare_part=part,
                    document=None,
                    relationship_type='component',
                    quantity=random.randint(1, 5),
                    position=f"Section {random.choice(['A', 'B', 'C', 'D'])}-{random.randint(1, 10)}",
                    criticality=random.choice([1, 2, 3, 4]),  # 1=Critical, 2=Important, 3=Normal, 4=Optional
                    notes=f"Standard component for {equipment.name}",
                    created_by=admin_user
                )
                relationship_count += 1
    
    # Create equipment-document relationships
    for doc_key, document in documents_dict.items():
        # Check if relationship already exists
        if not BOMRelationship.objects.filter(
            equipment=document.equipment,
            document=document,
            relationship_type='documentation'
        ).exists():
            # Create relationship with the document's equipment
            relationship = BOMRelationship.objects.create(
                id=uuid.uuid4(),
                equipment=document.equipment,
                spare_part=None,
                document=document,
                relationship_type='documentation',
                quantity=1,
                criticality=random.choice([1, 2, 3, 4]),  # 1=Critical, 2=Important, 3=Normal, 4=Optional
                notes=f"Documentation for {document.equipment.name}",
                created_by=admin_user
            )
            relationship_count += 1
    
    print(f"Created {relationship_count} BOM relationships")

# Create equipment spare part usage records
def create_part_usage(equipment_dict, parts_dict, admin_user):
    usage_count = 0
    
    # Sample usage data
    usage_data = [
        {
            'equipment': 'EQ-MLT-001',
            'part': 'MTR-001',
            'status': 'installed',
            'position': 'Main Drive',
            'installation_date': timezone.now() - datetime.timedelta(days=random.randint(90, 365)),
            'serial_number': 'MTR-2023-001',
            'notes': 'Main drive motor installed during scheduled maintenance'
        },
        {
            'equipment': 'EQ-MLT-001',
            'part': 'SNS-001',
            'status': 'installed',
            'position': 'Temperature Control',
            'installation_date': timezone.now() - datetime.timedelta(days=random.randint(90, 365)),
            'serial_number': 'SNS-2023-101',
            'notes': 'Temperature monitoring sensors installed during commissioning'
        },
        {
            'equipment': 'EQ-CST-001',
            'part': 'BRG-001',
            'status': 'installed',
            'position': 'Roller Assembly',
            'installation_date': timezone.now() - datetime.timedelta(days=random.randint(180, 365)),
            'serial_number': 'BRG-2022-045',
            'notes': 'Main roller bearings installed during last overhaul'
        },
        {
            'equipment': 'EQ-CST-001',
            'part': 'VLV-001',
            'status': 'installed',
            'position': 'Hydraulic Control',
            'installation_date': timezone.now() - datetime.timedelta(days=random.randint(90, 180)),
            'serial_number': 'VLV-2023-023',
            'notes': 'Control valves for hydraulic system installed during upgrade'
        }
    ]
    
    # Create usage records
    for usage in usage_data:
        if usage['equipment'] not in equipment_dict or usage['part'] not in parts_dict:
            continue
            
        equipment = equipment_dict[usage['equipment']]
        part = parts_dict[usage['part']]
        
        # Check if usage with same equipment, part, and position already exists
        existing = EquipmentSparePartUsage.objects.filter(
            equipment=equipment,
            spare_part=part,
            position=usage['position']
        ).first()
        
        if not existing:
            usage_obj = EquipmentSparePartUsage.objects.create(
                id=uuid.uuid4(),
                equipment=equipment,
                spare_part=part,
                status=usage['status'],
                position=usage['position'],
                installation_date=usage['installation_date'],
                serial_number=usage['serial_number'],
                notes=usage['notes'],
                created_by=admin_user
            )
            usage_count += 1
            
    print(f"Created {usage_count} spare part usage records")

# Add new function to create full hierarchical structure
@transaction.atomic
def create_hierarchical_data():
    """
    Creates a complete hierarchical data structure linking:
    - Areas -> Sub-areas
    - Areas -> Equipment -> Sub-equipment (child equipment)
    - Equipment -> Spare parts
    
    This shows the complete parent-child relationships in the system.
    """
    print("\n=== Creating hierarchical data structure ===")
    admin_user = get_or_create_admin()
    
    # Step 1: Create hierarchical area structure (plant -> sections -> departments)
    print("\nCreating hierarchical area structure...")
    
    # Main plant
    plant_area = Area.objects.create(
        id=uuid.uuid4(),
        code="PLANT-01",
        name="Steel Manufacturing Plant",
        description="Main manufacturing facility"
    )
    
    # Main sections (children of plant)
    production_area = Area.objects.create(
        id=uuid.uuid4(),
        code="PROD-MAIN",
        name="Production Department",
        description="Main production operations",
        parent=plant_area
    )
    
    maintenance_area = Area.objects.create(
        id=uuid.uuid4(),
        code="MAINT-MAIN",
        name="Maintenance Department",
        description="Equipment maintenance facilities",
        parent=plant_area
    )
    
    # Sub-sections (children of production)
    melting_area = Area.objects.create(
        id=uuid.uuid4(),
        code="PROD-MELT",
        name="Melting Operations",
        description="Melting furnaces and equipment",
        parent=production_area
    )
    
    casting_area = Area.objects.create(
        id=uuid.uuid4(),
        code="PROD-CAST",
        name="Casting Operations",
        description="Continuous casting equipment",
        parent=production_area
    )
    
    # Sub-sections (children of maintenance)
    workshop_area = Area.objects.create(
        id=uuid.uuid4(),
        code="MAINT-SHOP",
        name="Maintenance Workshop",
        description="Equipment repair facilities",
        parent=maintenance_area
    )
    
    print(f"Created area hierarchy: Plant -> Departments -> Sections")
    
    # Step 2: Create hierarchical equipment structure
    print("\nCreating hierarchical equipment structure...")
    
    # Main furnace (in melting area)
    furnace = Equipment.objects.create(
        id=uuid.uuid4(),
        code="EQ-FURN-01",
        name="Electric Arc Furnace #1",
        equipment_type="machine",
        area=melting_area,
        manufacturer="Steel Systems Inc.",
        model="EAF-5000",
        serial_number="SS-EAF-12345",
        installation_date=timezone.now() - datetime.timedelta(days=365),
        status="operational",
        description="Main electric arc furnace for steel production",
        is_critical=True,
        purchase_cost=3500000.00,
        created_by=admin_user,
        updated_by=admin_user
    )
    
    # Child equipment of furnace - Control system
    control_system = Equipment.objects.create(
        id=uuid.uuid4(),
        code="EQ-FURN-01-CTRL",
        name="Furnace Control System",
        equipment_type="system",
        area=melting_area,
        parent=furnace,  # This links it as child of furnace
        manufacturer="Control Solutions Ltd.",
        model="FCS-800",
        serial_number="CS-FCS-54321",
        installation_date=timezone.now() - datetime.timedelta(days=365),
        status="operational",
        description="Main control system for electric arc furnace",
        is_critical=True,
        purchase_cost=750000.00,
        created_by=admin_user,
        updated_by=admin_user
    )
    
    # Child equipment of control system - PLC
    plc_system = Equipment.objects.create(
        id=uuid.uuid4(),
        code="EQ-FURN-01-CTRL-PLC",
        name="Furnace PLC Controller",
        equipment_type="component",
        area=melting_area,
        parent=control_system,  # This links it as child of control system
        manufacturer="Siemens",
        model="S7-1500",
        serial_number="SIE-S7-78901",
        installation_date=timezone.now() - datetime.timedelta(days=365),
        status="operational",
        description="PLC controller for furnace operations",
        is_critical=True,
        purchase_cost=85000.00,
        created_by=admin_user,
        updated_by=admin_user
    )
    
    # Main casting machine (in casting area)
    caster = Equipment.objects.create(
        id=uuid.uuid4(),
        code="EQ-CAST-01",
        name="Continuous Casting Machine #1",
        equipment_type="machine",
        area=casting_area,
        manufacturer="MetalCast Systems",
        model="CC-2000",
        serial_number="MC-CC-54321",
        installation_date=timezone.now() - datetime.timedelta(days=300),
        status="operational",
        description="Main continuous casting machine for billets",
        is_critical=True,
        purchase_cost=2800000.00,
        created_by=admin_user,
        updated_by=admin_user
    )
    
    # Child equipment of caster - Cooling system
    cooling_system = Equipment.objects.create(
        id=uuid.uuid4(),
        code="EQ-CAST-01-COOL",
        name="Caster Cooling System",
        equipment_type="system",
        area=casting_area,
        parent=caster,  # This links it as child of caster
        manufacturer="CoolTech Systems",
        model="CS-500",
        serial_number="CT-CS-12345",
        installation_date=timezone.now() - datetime.timedelta(days=300),
        status="operational",
        description="Water cooling system for continuous caster",
        is_critical=True,
        purchase_cost=450000.00,
        created_by=admin_user,
        updated_by=admin_user
    )
    
    print(f"Created equipment hierarchy: Machine -> Systems -> Components")
    
    # Step 3: Create spare part categories with hierarchy
    print("\nCreating spare part category hierarchy...")
    
    # Main categories
    electrical_cat = Category.objects.create(
        id=uuid.uuid4(),
        code="ELEC-MAIN",
        name="Electrical Components",
        description="All electrical parts and systems",
        created_by=admin_user
    )
    
    mechanical_cat = Category.objects.create(
        id=uuid.uuid4(),
        code="MECH-MAIN",
        name="Mechanical Components",
        description="All mechanical parts and systems",
        created_by=admin_user
    )
    
    # Sub-categories for electrical
    motors_cat = Category.objects.create(
        id=uuid.uuid4(),
        code="ELEC-MOTOR",
        name="Electric Motors",
        description="All types of electric motors",
        parent=electrical_cat,
        created_by=admin_user
    )
    
    controllers_cat = Category.objects.create(
        id=uuid.uuid4(),
        code="ELEC-CTRL",
        name="Controllers and Automation",
        description="PLCs, control cards and automation components",
        parent=electrical_cat,
        created_by=admin_user
    )
    
    # Sub-categories for mechanical
    bearings_cat = Category.objects.create(
        id=uuid.uuid4(),
        code="MECH-BEAR",
        name="Bearings",
        description="All types of bearings",
        parent=mechanical_cat,
        created_by=admin_user
    )
    
    hydraulic_cat = Category.objects.create(
        id=uuid.uuid4(),
        code="MECH-HYD",
        name="Hydraulic Components",
        description="Pumps, valves and hydraulic components",
        parent=mechanical_cat,
        created_by=admin_user
    )
    
    print(f"Created category hierarchy: Main Category -> Sub-categories")
    
    # Step 4: Create spare parts and assign to categories
    print("\nCreating spare parts for each category...")
    
    # Motor for furnace
    furnace_motor = SparePart.objects.create(
        id=uuid.uuid4(),
        code="SP-MOTOR-01",
        name="Main Drive Motor 150kW",
        category=motors_cat,
        description="Main drive motor for electric arc furnace",
        price=28500.00,
        minimum_stock=1,
        current_stock=2,
        unit="pcs",
        location="Main Warehouse A5",
        manufacturer="ABB",
        supplier="Industrial Motors Inc.",
        supplier_reference="ABB-150kW-01",
        lead_time=45,
        notes="Critical component - keep in stock",
        created_by=admin_user
    )
    
    # PLC for control system
    control_plc = SparePart.objects.create(
        id=uuid.uuid4(),
        code="SP-PLC-01",
        name="Siemens S7-1500 CPU",
        category=controllers_cat,
        description="PLC CPU for furnace control system",
        price=6750.00,
        minimum_stock=1,
        current_stock=2,
        unit="pcs",
        location="Main Warehouse B2",
        manufacturer="Siemens",
        supplier="Automation Supplies Ltd.",
        supplier_reference="S7-1500-CPU",
        lead_time=21,
        notes="Critical control component",
        created_by=admin_user
    )
    
    # Bearings for caster
    caster_bearing = SparePart.objects.create(
        id=uuid.uuid4(),
        code="SP-BEAR-01",
        name="Heavy Duty Roller Bearing 200mm",
        category=bearings_cat,
        description="Main roller bearing for continuous caster",
        price=5250.00,
        minimum_stock=2,
        current_stock=4,
        unit="pcs",
        location="Main Warehouse C3",
        manufacturer="SKF",
        supplier="Bearing Solutions Inc.",
        supplier_reference="SKF-200HD-01",
        lead_time=30,
        notes="Heavy duty bearing for high temperature application",
        created_by=admin_user
    )
    
    # Pump for cooling system
    cooling_pump = SparePart.objects.create(
        id=uuid.uuid4(),
        code="SP-PUMP-01",
        name="High Capacity Water Pump 1000L/min",
        category=hydraulic_cat,
        description="Main cooling water pump for caster cooling system",
        price=12500.00,
        minimum_stock=1,
        current_stock=2,
        unit="pcs",
        location="Main Warehouse D1",
        manufacturer="Grundfos",
        supplier="Pump Supply Co.",
        supplier_reference="GF-1000L-01",
        lead_time=35,
        notes="High capacity industrial cooling pump",
        created_by=admin_user
    )
    
    print(f"Created spare parts for each category")
    
    # Step 5: Link spare parts to equipment with BOM relationships
    print("\nCreating equipment-spare part relationships...")
    
    # Link motor to furnace
    BOMRelationship.objects.create(
        id=uuid.uuid4(),
        equipment=furnace,
        spare_part=furnace_motor,
        relationship_type='component',
        quantity=1,
        position="Main Drive Section",
        criticality=1,  # Critical
        notes="Main drive motor for the furnace",
        created_by=admin_user
    )
    
    # Link PLC to control system
    BOMRelationship.objects.create(
        id=uuid.uuid4(),
        equipment=control_system,
        spare_part=control_plc,
        relationship_type='component',
        quantity=1,
        position="Control Cabinet",
        criticality=1,  # Critical
        notes="Primary PLC controller",
        created_by=admin_user
    )
    
    # Link bearings to caster
    BOMRelationship.objects.create(
        id=uuid.uuid4(),
        equipment=caster,
        spare_part=caster_bearing,
        relationship_type='component',
        quantity=8,
        position="Main Roller Assembly",
        criticality=1,  # Critical
        notes="Main support bearings for rollers",
        created_by=admin_user
    )
    
    # Link pump to cooling system
    BOMRelationship.objects.create(
        id=uuid.uuid4(),
        equipment=cooling_system,
        spare_part=cooling_pump,
        relationship_type='component',
        quantity=2,
        position="Pump Station",
        criticality=1,  # Critical
        notes="Primary and backup cooling pumps",
        created_by=admin_user
    )
    
    print(f"Created BOM relationships linking equipment and spare parts")
    
    # Step 6: Create usage records for tracking installed parts
    print("\nCreating part usage records...")
    
    # Record motor installed in furnace
    EquipmentSparePartUsage.objects.create(
        id=uuid.uuid4(),
        equipment=furnace,
        spare_part=furnace_motor,
        status='installed',
        position='Main Drive',
        installation_date=timezone.now() - datetime.timedelta(days=365),
        serial_number='ABB-2022-001',
        notes='Original motor installed during commissioning',
        created_by=admin_user
    )
    
    # Record PLC installed in control system
    EquipmentSparePartUsage.objects.create(
        id=uuid.uuid4(),
        equipment=control_system,
        spare_part=control_plc,
        status='installed',
        position='Control Cabinet',
        installation_date=timezone.now() - datetime.timedelta(days=365),
        serial_number='S7-2022-001',
        notes='Original PLC installed during commissioning',
        created_by=admin_user
    )
    
    # Record bearing installed in caster
    EquipmentSparePartUsage.objects.create(
        id=uuid.uuid4(),
        equipment=caster,
        spare_part=caster_bearing,
        status='installed',
        position='Roller Assembly 1',
        installation_date=timezone.now() - datetime.timedelta(days=300),
        serial_number='SKF-2022-001',
        notes='Original bearing installed during commissioning',
        created_by=admin_user
    )
    
    # Record pump installed in cooling system
    EquipmentSparePartUsage.objects.create(
        id=uuid.uuid4(),
        equipment=cooling_system,
        spare_part=cooling_pump,
        status='installed',
        position='Primary Pump',
        installation_date=timezone.now() - datetime.timedelta(days=300),
        serial_number='GF-2022-001',
        notes='Original pump installed during commissioning',
        created_by=admin_user
    )
    
    print(f"Created usage records for installed spare parts")
    
    print("\n=== Hierarchical data structure creation complete ===")
    return True

# Main function to create all data
def create_all_data():
    try:
        print("Creating dummy data for SSBDM with PostgreSQL...")
        
        # Create hierarchical data structure (new approach)
        create_hierarchical_data()
        
        # Create additional standard data if desired
        # admin_user = get_or_create_admin()
        # technicians_dict = create_technicians()
        # areas_dict = create_areas()
        # equipment_dict = create_equipment(areas_dict, admin_user)
        # create_specifications(equipment_dict, admin_user)
        # categories_dict = create_spare_part_categories(admin_user)
        # parts_dict = create_spare_parts(categories_dict, admin_user)
        # create_spare_part_transactions(parts_dict, equipment_dict, technicians_dict)
        # doc_categories_dict = create_document_categories(admin_user)
        # documents_dict = create_documents(equipment_dict, doc_categories_dict, admin_user)
        # create_relationships(equipment_dict, parts_dict, documents_dict, admin_user)
        # create_part_usage(equipment_dict, parts_dict, admin_user)
        
        # Verify data was created
        verify_data()
        
        print("Dummy data creation complete!")
    except Exception as e:
        print(f"ERROR: Failed to create dummy data: {e}")
        traceback.print_exc()
        return False
    return True

def verify_data():
    """Verify that data was actually created in the database"""
    print("\nVerifying created data:")
    print(f"- Users: {User.objects.count()}")
    print(f"- Areas: {Area.objects.count()}")
    print(f"- Equipment: {Equipment.objects.count()}")
    print(f"- Technical Specifications: {TechnicalSpecification.objects.count()}")
    print(f"- Categories: {Category.objects.count()}")
    print(f"- Spare Parts: {SparePart.objects.count()}")
    print(f"- Transactions: {SparePartTransaction.objects.count()}")
    print(f"- Document Categories: {DocumentCategory.objects.count()}")
    print(f"- Documents: {EquipmentDocument.objects.count()}")
    print(f"- BOM Relationships: {BOMRelationship.objects.count()}")
    print(f"- Part Usages: {EquipmentSparePartUsage.objects.count()}")

if __name__ == "__main__":
    success = create_all_data()
    if not success:
        sys.exit(1) 