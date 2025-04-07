import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction

from spare_parts.models import Category, SparePart, SparePartTransaction
from equipment.models import Area, Equipment


class Command(BaseCommand):
    help = 'Creates dummy data for testing the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=int,
            default=10,
            help='Number of categories to create'
        )
        parser.add_argument(
            '--spare_parts',
            type=int,
            default=30,
            help='Number of spare parts to create'
        )
        parser.add_argument(
            '--transactions',
            type=int,
            default=50,
            help='Number of transactions to create'
        )

    def handle(self, *args, **options):
        # Get or create a test user
        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.stdout.write('Creating admin user...')
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
        
        # Start transaction for faster database operations
        with transaction.atomic():
            # Create categories
            self.create_categories(options['categories'])
            
            # Create spare parts
            self.create_spare_parts(options['spare_parts'])
            
            # Create transactions for spare parts
            self.create_transactions(options['transactions'], user)
        
        self.stdout.write(self.style.SUCCESS('Successfully created dummy data!'))
        
        # Print summary
        self.stdout.write('\nSummary:')
        self.stdout.write(f'Categories: {Category.objects.count()}')
        self.stdout.write(f'Spare Parts: {SparePart.objects.count()}')
        self.stdout.write(f'Transactions: {SparePartTransaction.objects.count()}')
        self.stdout.write(f'Areas: {Area.objects.count()}')
        self.stdout.write(f'Equipment: {Equipment.objects.count()}')
    
    def create_categories(self, count):
        """Create hierarchy of categories"""
        self.stdout.write('Creating categories...')
        
        # Create main categories
        main_categories = []
        for i in range(count // 3):
            name = random.choice([
                'Electrical', 'Mechanical', 'Hydraulic', 'Pneumatic', 
                'Electronic', 'Engine', 'Transmission', 'Fasteners',
                'Tools', 'Consumables', 'Safety Equipment', 'Instrumentation'
            ] + [f'Category {i+1}'])
            
            if not Category.objects.filter(name=name).exists():
                category = Category.objects.create(
                    name=name,
                    description=f'This is the {name} category for spare parts.'
                )
                main_categories.append(category)
                self.stdout.write(f'  Created main category: {name}')
        
        # Create subcategories
        for main_category in main_categories:
            num_subcategories = random.randint(1, 3)
            for i in range(num_subcategories):
                name = f'{main_category.name} - Subcategory {i+1}'
                if not Category.objects.filter(name=name).exists():
                    subcategory = Category.objects.create(
                        name=name,
                        description=f'This is a subcategory of {main_category.name}.',
                        parent=main_category
                    )
                    self.stdout.write(f'    Created subcategory: {name}')
    
    def create_spare_parts(self, count):
        """Create spare parts and associate with categories"""
        self.stdout.write('Creating spare parts...')
        
        categories = list(Category.objects.all())
        if not categories:
            self.stdout.write(self.style.WARNING('No categories found. Creating a default category.'))
            categories = [Category.objects.create(name='Default Category')]
        
        # Create or get equipment and areas
        if not Area.objects.exists():
            self.create_areas_and_equipment()
        
        equipment_list = list(Equipment.objects.all())
        
        manufacturers = ['ABB', 'Siemens', 'GE', 'Schneider', 'Allen-Bradley', 'Honeywell', 'Emerson', 'Yokogawa', 'Mitsubishi', 'Bosch']
        
        for i in range(count):
            part_number = f'P{random.randint(1000, 9999)}'
            description = random.choice([
                'Motor', 'Pump', 'Valve', 'Sensor', 'Switch', 'Bearing', 
                'Relay', 'Gasket', 'O-Ring', 'Filter', 'Circuit Board',
                'Battery', 'Connector', 'Cable', 'Fuse', 'Belt', 'Gear'
            ]) + f' Type {random.choice(["A", "B", "C", "D"])}'
            
            if not SparePart.objects.filter(part_number=part_number).exists():
                quantity = random.randint(0, 30)
                minimum = random.randint(5, 15)
                spare_part = SparePart.objects.create(
                    part_number=part_number,
                    description=description,
                    quantity_in_stock=quantity,
                    minimum_stock=minimum,
                    unit_price=round(random.uniform(10, 1000), 2),
                    location=f'Rack {random.randint(1, 20)}, Bin {random.randint(1, 50)}',
                    supplier=random.choice(['Acme Inc.', 'Globex Corp.', 'Stark Industries', 'Wayne Enterprises', 'Umbrella Corp.']),
                    notes=f'This is a note about {description}.',
                    category=random.choice(categories)
                )
                
                # Associate with random equipment (0-3 pieces)
                if equipment_list:
                    for _ in range(random.randint(0, 3)):
                        if equipment_list:
                            spare_part.equipment.add(random.choice(equipment_list))
                
                self.stdout.write(f'  Created spare part: {part_number} - {description}')
    
    def create_transactions(self, count, user):
        """Create transaction history for spare parts"""
        self.stdout.write('Creating transactions...')
        
        spare_parts = list(SparePart.objects.all())
        if not spare_parts:
            self.stdout.write(self.style.WARNING('No spare parts found. Skipping transactions.'))
            return
        
        transaction_types = ['received', 'issued', 'returned', 'adjusted']
        # Don't include None in references since we have a NOT NULL constraint
        references = ['WO-12345', 'PO-98765', 'REQ-54321', 'INV-11111', 'ADJ-22222', 'N/A']
        
        for i in range(count):
            part = random.choice(spare_parts)
            transaction_type = random.choice(transaction_types)
            
            # Make more realistic quantities
            if transaction_type == 'received':
                quantity = random.randint(5, 20)
            elif transaction_type == 'issued':
                quantity = random.randint(1, 5)
            elif transaction_type == 'returned':
                quantity = random.randint(1, 3)
            else:  # adjusted
                quantity = random.randint(-5, 5)
            
            # Create transaction with a date in the past
            days_ago = random.randint(1, 90)
            transaction_date = timezone.now() - timedelta(days=days_ago)
            
            transaction = SparePartTransaction.objects.create(
                spare_part=part,
                transaction_type=transaction_type,
                quantity=abs(quantity),  # ensure positive for DB consistency
                date=transaction_date,
                performed_by=user,
                notes=f'{"Test transaction" if i % 5 == 0 else ""}',
                reference=random.choice(references)
            )
            
            # Update stock quantity (bypassing the model save logic)
            if i % 10 == 0:
                self.stdout.write(f'  Created transaction: {transaction}')
    
    def create_areas_and_equipment(self):
        """Create areas and equipment if they don't exist"""
        self.stdout.write('Creating areas and equipment...')
        
        # Create main areas
        main_areas = []
        for name in ['Production', 'Maintenance', 'Storage', 'Utilities', 'Office']:
            area = Area.objects.create(
                code=name[:3].upper(),
                name=name,
                description=f'{name} area of the facility'
            )
            main_areas.append(area)
            self.stdout.write(f'  Created area: {name}')
            
            # Create sub-areas
            if name == 'Production':
                for sub_name in ['Assembly Line A', 'Assembly Line B', 'Packaging', 'Quality Control']:
                    sub_area = Area.objects.create(
                        code=f'{name[:3]}-{sub_name[:3]}',
                        name=sub_name,
                        description=f'{sub_name} sub-area',
                        parent=area
                    )
                    self.stdout.write(f'    Created sub-area: {sub_name}')
            
            elif name == 'Maintenance':
                for sub_name in ['Workshop', 'Tool Room', 'Calibration Lab']:
                    sub_area = Area.objects.create(
                        code=f'{name[:3]}-{sub_name[:3]}',
                        name=sub_name,
                        description=f'{sub_name} sub-area',
                        parent=area
                    )
                    self.stdout.write(f'    Created sub-area: {sub_name}')
        
        # Create equipment
        areas = Area.objects.all()
        
        equipment_types = ['machine', 'component', 'tool', 'system']
        status_choices = ['operational', 'maintenance', 'out_of_service']
        
        equipment_list = [
            ('CNC-001', 'CNC Machine 1', 'machine'),
            ('PRE-001', 'Hydraulic Press', 'machine'),
            ('BOI-001', 'Boiler System', 'system'),
            ('COM-001', 'Air Compressor', 'machine'),
            ('ROB-001', 'Robotic Arm', 'machine'),
            ('GEN-001', 'Backup Generator', 'system'),
            ('CON-001', 'Control System', 'system'),
            ('MOT-001', 'Electric Motor 15kW', 'component'),
            ('PUM-001', 'Cooling Pump', 'component'),
            ('DRI-001', 'Drive Assembly', 'component'),
            ('TOO-001', 'Drill Press', 'tool'),
            ('TOO-002', 'Lathe Machine', 'tool'),
        ]
        
        # Create main equipment
        created_equipment = []
        for code, name, type in equipment_list:
            area = random.choice(areas)
            equipment = Equipment.objects.create(
                code=code,
                name=name,
                equipment_type=type,
                area=area,
                manufacturer=random.choice(['ABB', 'Siemens', 'GE', 'Bosch', 'Allen-Bradley']),
                model=f'Model {random.choice(["A", "B", "C", "D"])}-{random.randint(100, 999)}',
                serial_number=f'SN-{random.randint(10000, 99999)}',
                installation_date=timezone.now() - timedelta(days=random.randint(30, 1000)),
                status=random.choice(status_choices),
                description=f'This is a {name} used for manufacturing operations.'
            )
            created_equipment.append(equipment)
            self.stdout.write(f'  Created equipment: {code} - {name}')
        
        # Create components for some equipment
        for i, equipment in enumerate(created_equipment):
            if equipment.equipment_type == 'machine' or equipment.equipment_type == 'system':
                for j in range(random.randint(1, 3)):
                    component_name = random.choice([
                        'Control Board', 'Motor', 'Power Supply', 'Sensor Array', 
                        'Pump', 'Valve Assembly', 'Drive System', 'Cooling Unit'
                    ])
                    component = Equipment.objects.create(
                        code=f'CMP-{random.randint(1000, 9999)}',
                        name=f'{component_name} for {equipment.name}',
                        equipment_type='component',
                        area=equipment.area,
                        parent=equipment,
                        manufacturer=equipment.manufacturer,
                        model=f'Component {random.choice(["X", "Y", "Z"])}-{random.randint(100, 999)}',
                        serial_number=f'SN-{random.randint(10000, 99999)}',
                        installation_date=equipment.installation_date + timedelta(days=random.randint(1, 10)),
                        status=equipment.status,
                        description=f'This is a {component_name} component of {equipment.name}.'
                    )
                    self.stdout.write(f'    Created component: {component.code} - {component.name}') 