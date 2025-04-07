import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSBDM.settings')
django.setup()

from django.contrib.auth.models import User
from equipment_new.models import Area, Equipment, TechnicalSpecification
from spare_parts.models import Category, SparePart
from documents.models import DocumentCategory, EquipmentDocument
from django.utils import timezone
import datetime

# Check if areas exist already
if Area.objects.count() == 0:
    print("Creating sample areas...")
    # Create parent areas
    production = Area.objects.create(
        code="PROD",
        name="Production",
        description="Main production area",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    maintenance = Area.objects.create(
        code="MAINT",
        name="Maintenance",
        description="Maintenance workshop",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    storage = Area.objects.create(
        code="STOR",
        name="Storage",
        description="Storage areas",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    # Create sub-areas
    Area.objects.create(
        code="PROD-A",
        name="Production Line A",
        description="First production line",
        parent=production,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    Area.objects.create(
        code="PROD-B",
        name="Production Line B",
        description="Second production line",
        parent=production,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

    Area.objects.create(
        code="STOR-SP",
        name="Spare Parts Storage",
        description="Storage for spare parts",
        parent=storage,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

# Check if equipment exists already
if Equipment.objects.count() == 0:
    print("Creating sample equipment...")
    
    # Get some areas
    try:
        prod_area = Area.objects.get(code="PROD-A")
        maint_area = Area.objects.get(code="MAINT")
        
        # Create equipment
        crane = Equipment.objects.create(
            code="EQ-CR01",
            name="Overhead Crane",
            equipment_type="Mechanical",
            manufacturer="Crane Co.",
            model="HC-5000",
            serial_number="CR12345",
            installation_date=datetime.date(2020, 3, 15),
            last_maintenance_date=datetime.date(2023, 8, 10),
            status="Operational",
            description="Main overhead crane for moving materials",
            area=prod_area,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        motor = Equipment.objects.create(
            code="EQ-MT01",
            name="Electric Motor",
            equipment_type="Electrical",
            manufacturer="ElectMotors Inc.",
            model="EM-200",
            serial_number="EM98765",
            installation_date=datetime.date(2021, 5, 20),
            last_maintenance_date=datetime.date(2023, 9, 5),
            status="Operational",
            description="Main drive motor for conveyor system",
            area=prod_area,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Create technical specifications
        TechnicalSpecification.objects.create(
            equipment=crane,
            specification="Load Capacity",
            unit="Tons",
            value="10",
            created_at=timezone.now(),
            last_updated=timezone.now()
        )
        
        TechnicalSpecification.objects.create(
            equipment=crane,
            specification="Span",
            unit="Meters",
            value="25",
            created_at=timezone.now(),
            last_updated=timezone.now()
        )
        
        TechnicalSpecification.objects.create(
            equipment=motor,
            specification="Power",
            unit="kW",
            value="55",
            created_at=timezone.now(),
            last_updated=timezone.now()
        )
        
        TechnicalSpecification.objects.create(
            equipment=motor,
            specification="Voltage",
            unit="V",
            value="380",
            created_at=timezone.now(),
            last_updated=timezone.now()
        )
    except Area.DoesNotExist:
        print("Required areas not found. Please create areas first.")

# Check if spare part categories exist
if Category.objects.count() == 0:
    print("Creating spare part categories...")
    
    # Create parent categories
    electrical = Category.objects.create(
        name="Electrical",
        description="Electrical components and parts",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    mechanical = Category.objects.create(
        name="Mechanical",
        description="Mechanical components and parts",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    # Create subcategories
    Category.objects.create(
        name="Motors",
        description="Electric motors of all types",
        parent=electrical,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    Category.objects.create(
        name="Bearings",
        description="All types of bearings",
        parent=mechanical,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

# Check if spare parts exist
if SparePart.objects.count() == 0:
    print("Creating sample spare parts...")
    
    try:
        elec_cat = Category.objects.get(name="Electrical")
        motor_cat = Category.objects.get(name="Motors")
        mech_cat = Category.objects.get(name="Mechanical")
        bear_cat = Category.objects.get(name="Bearings")
        
        # Create spare parts
        SparePart.objects.create(
            part_number="SP-BRG-001",
            description="Ball Bearing 6205",
            quantity_in_stock=25,
            minimum_stock=10,
            location="Rack A-12",
            notes="Standard bearing for conveyor rollers",
            supplier="Bearing Supplies Ltd.",
            category=bear_cat,
            unit_price=15.50,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            last_updated=timezone.now()
        )
        
        SparePart.objects.create(
            part_number="SP-MTR-001",
            description="Motor Contactor 40A",
            quantity_in_stock=5,
            minimum_stock=2,
            location="Rack E-03",
            notes="Used in control panels for main motors",
            supplier="Electrical Parts Inc.",
            category=elec_cat,
            unit_price=85.75,
            created_at=timezone.now(),
            updated_at=timezone.now(),
            last_updated=timezone.now()
        )
    except Category.DoesNotExist:
        print("Required categories not found. Please create categories first.")

# Create document categories if they don't exist
if DocumentCategory.objects.count() == 0:
    print("Creating document categories...")
    
    DocumentCategory.objects.create(
        name="Manuals",
        description="Equipment manuals and documentation",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    DocumentCategory.objects.create(
        name="Drawings",
        description="Technical drawings and schematics",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    DocumentCategory.objects.create(
        name="Certificates",
        description="Certification and compliance documents",
        created_at=timezone.now(),
        updated_at=timezone.now()
    )

print("Sample data creation completed!") 