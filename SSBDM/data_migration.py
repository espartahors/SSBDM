"""
Data migration script to migrate data from old model structure to new structure.
This script should be run after the database has been migrated to the new structure.
"""
import os
import django
import uuid

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSBDM.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from equipment_new.models import Area, Equipment
from spare_parts.models import SparePart, Category
from documents.models import EquipmentDocument, DocumentCategory
from ssbom.models import BOMRelationship

def migrate_equipment_data():
    """Migrate equipment data to the new structure"""
    print("Migrating equipment data...")
    
    # Get admin user for metadata fields
    admin_user = User.objects.filter(is_superuser=True).first()
    
    # Migrate Areas
    # The area model structure is similar, just adding UUIDs
    areas = Area.objects.all()
    for area in areas:
        # Update with new UUID
        area.id = uuid.uuid4()
        area.save()
    
    # Migrate Equipment
    # Equipment model has more fields but structure is similar
    equipments = Equipment.objects.all()
    for equipment in equipments:
        # Update with new UUID
        equipment.id = uuid.uuid4()
        # Set created_by and updated_by
        equipment.created_by = admin_user
        equipment.updated_by = admin_user
        equipment.save()
    
    print(f"Migrated {areas.count()} areas and {equipments.count()} equipment records")

def migrate_spare_parts_data():
    """Migrate spare parts data to the new structure"""
    print("Migrating spare parts data...")
    
    # Get admin user for metadata fields
    admin_user = User.objects.filter(is_superuser=True).first()
    
    # Migrate Categories
    # Generating codes for categories
    categories = Category.objects.all()
    for idx, category in enumerate(categories):
        # Generate a code if it doesn't exist
        category.code = f"CAT-{idx+1:03d}"
        # Update with new UUID
        category.id = uuid.uuid4()
        # Set created_by and updated_by
        category.created_by = admin_user
        category.updated_by = admin_user
        category.save()
    
    # Migrate SpareParts
    # Need to handle renamed fields
    parts = SparePart.objects.all()
    for part in parts:
        # Update field values based on old model
        part.id = uuid.uuid4()
        # Map old field names to new field names
        part.code = part.part_number if hasattr(part, 'part_number') else f"PART-{uuid.uuid4().hex[:8]}"
        part.name = part.description[:200] if hasattr(part, 'description') else "Unknown Part"
        part.current_stock = part.quantity_in_stock if hasattr(part, 'quantity_in_stock') else 0
        part.price = part.unit_price if hasattr(part, 'unit_price') else None
        # Set default values for new fields
        part.unit = 'pcs'
        part.currency = 'USD'
        # Set created_by and updated_by
        part.created_by = admin_user
        part.updated_by = admin_user
        part.save()
        
        # Handle many-to-many relationships with equipment
        # In the new structure, these are handled through BOMRelationship
        if hasattr(part, 'equipment'):
            for equipment in part.equipment.all():
                # Create a BOMRelationship for each equipment
                BOMRelationship.objects.create(
                    equipment=equipment,
                    spare_part=part,
                    relationship_type='component',
                    quantity=1,
                    created_by=admin_user,
                    updated_by=admin_user
                )
    
    print(f"Migrated {categories.count()} categories and {parts.count()} spare parts")

def migrate_documents_data():
    """Migrate documents data to the new structure"""
    print("Migrating documents data...")
    
    # Get admin user for metadata fields
    admin_user = User.objects.filter(is_superuser=True).first()
    
    # Create a default document category if none exists
    default_category, created = DocumentCategory.objects.get_or_create(
        name="General Documents",
        defaults={
            'id': uuid.uuid4(),
            'code': 'DOC-GEN',
            'description': 'Default category for general documents',
            'created_by': admin_user,
            'updated_by': admin_user
        }
    )
    
    # Migrate document categories
    categories = DocumentCategory.objects.all()
    for idx, category in enumerate(categories):
        if not hasattr(category, 'code') or not category.code:
            category.code = f"DOC-{idx+1:03d}"
        if not hasattr(category, 'id') or not category.id:
            category.id = uuid.uuid4()
        # Set created_by and updated_by
        category.created_by = admin_user
        category.updated_by = admin_user
        category.save()
    
    # Migrate documents
    documents = EquipmentDocument.objects.all()
    for doc in documents:
        # Update with new UUID
        doc.id = uuid.uuid4()
        # Set default category if none
        if not hasattr(doc, 'category') or not doc.category:
            doc.category = default_category
        # Map version to revision if needed
        if hasattr(doc, 'version'):
            doc.revision = doc.version
        # Set created_by and updated_by
        doc.updated_by = admin_user
        doc.save()
    
    print(f"Migrated {categories.count()} document categories and {documents.count()} documents")

def migrate_relationships():
    """Migrate relationship data to the new structure"""
    print("Migrating relationship data...")
    
    # Get admin user for metadata fields
    admin_user = User.objects.filter(is_superuser=True).first()
    
    # BOMRelationships should already be migrated by the spare parts migration
    # Just need to update any missing UUIDs
    relationships = BOMRelationship.objects.all()
    for rel in relationships:
        if not hasattr(rel, 'id') or not rel.id:
            rel.id = uuid.uuid4()
        # Set created_by and updated_by
        rel.created_by = admin_user
        rel.updated_by = admin_user
        rel.save()
    
    print(f"Migrated {relationships.count()} relationships")

@transaction.atomic
def run_migration():
    """Run the complete migration"""
    try:
        print("Starting data migration...")
        migrate_equipment_data()
        migrate_spare_parts_data()
        migrate_documents_data()
        migrate_relationships()
        print("Data migration completed successfully")
    except Exception as e:
        print(f"Error during migration: {e}")
        # The transaction.atomic decorator will rollback all changes if an exception occurs

if __name__ == "__main__":
    run_migration() 