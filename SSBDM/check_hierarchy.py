#!/usr/bin/env python
"""
Script to check the hierarchical structure in the database.
"""
import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSBDM.settings')
import django
django.setup()

from equipment_new.models import Area, Equipment
from spare_parts.models import Category, SparePart
from ssbom.models import BOMRelationship, EquipmentSparePartUsage

def print_area_hierarchy():
    print("\n--- AREA HIERARCHY ---")
    # Get top-level (parent-less) areas
    main_areas = Area.objects.filter(parent=None)
    print(f"Found {main_areas.count()} main areas")
    
    for area in main_areas:
        print(f"\n* {area.name} [{area.code}]")
        
        # Get sub-areas (first level)
        sub_areas = Area.objects.filter(parent=area)
        for sub_area in sub_areas:
            print(f"  - {sub_area.name} [{sub_area.code}]")
            
            # Get sub-sub-areas (second level)
            sub_sub_areas = Area.objects.filter(parent=sub_area)
            for sub_sub_area in sub_sub_areas:
                print(f"    > {sub_sub_area.name} [{sub_sub_area.code}]")

def print_equipment_hierarchy():
    print("\n--- EQUIPMENT HIERARCHY ---")
    # Get top-level (parent-less) equipment
    main_equipment = Equipment.objects.filter(parent=None)
    print(f"Found {main_equipment.count()} main equipment items")
    
    for equip in main_equipment:
        print(f"\n* {equip.name} [{equip.code}] - {equip.area.name}")
        
        # Get sub-equipment (first level)
        sub_equip = Equipment.objects.filter(parent=equip)
        for sub in sub_equip:
            print(f"  - {sub.name} [{sub.code}]")
            
            # Get sub-sub-equipment (second level)
            sub_sub_equip = Equipment.objects.filter(parent=sub)
            for sub_sub in sub_sub_equip:
                print(f"    > {sub_sub.name} [{sub_sub.code}]")

def print_category_hierarchy():
    print("\n--- SPARE PART CATEGORY HIERARCHY ---")
    # Get top-level (parent-less) categories
    main_categories = Category.objects.filter(parent=None)
    print(f"Found {main_categories.count()} main categories")
    
    for cat in main_categories:
        print(f"\n* {cat.name} [{cat.code}]")
        
        # Get sub-categories
        sub_cats = Category.objects.filter(parent=cat)
        for sub in sub_cats:
            print(f"  - {sub.name} [{sub.code}]")
            
            # Get sub-sub-categories
            sub_sub_cats = Category.objects.filter(parent=sub)
            for sub_sub in sub_sub_cats:
                print(f"    > {sub_sub.name} [{sub_sub.code}]")

def print_equipment_parts_relationships():
    print("\n--- EQUIPMENT-SPARE PART RELATIONSHIPS ---")
    
    # Find equipment with spare parts
    equipment_ids = BOMRelationship.objects.filter(spare_part__isnull=False).values_list('equipment_id', flat=True).distinct()
    equipment_with_parts = Equipment.objects.filter(id__in=equipment_ids)
    print(f"Found {equipment_with_parts.count()} equipment items with spare parts")
    
    for equip in equipment_with_parts:
        print(f"\n* {equip.name} [{equip.code}]")
        
        # Get related spare parts
        relationships = BOMRelationship.objects.filter(
            equipment=equip, 
            spare_part__isnull=False
        )
        
        for rel in relationships:
            part = rel.spare_part
            print(f"  - Part: {part.name} [{part.code}]")
            print(f"    Category: {part.category.name}")
            print(f"    Quantity: {rel.quantity}")
            print(f"    Position: {rel.position}")
            
            # Check if this part is installed
            usages = EquipmentSparePartUsage.objects.filter(
                equipment=equip,
                spare_part=part
            )
            
            if usages.exists():
                for usage in usages:
                    print(f"    INSTALLED: {usage.position} (S/N: {usage.serial_number})")

def print_complete_hierarchy():
    """Prints the complete hierarchical structure from areas to equipment to spare parts"""
    print("\n=== COMPLETE HIERARCHICAL STRUCTURE ===\n")
    
    # Get top-level areas
    main_areas = Area.objects.filter(parent=None)
    
    for area in main_areas:
        print(f"AREA: {area.name} [{area.code}]")
        
        # Get sub-areas
        sub_areas = Area.objects.filter(parent=area)
        for sub_area in sub_areas:
            print(f"  └── SUB-AREA: {sub_area.name} [{sub_area.code}]")
            
            # Get equipment in this sub-area
            equipment_list = Equipment.objects.filter(area=sub_area, parent=None)
            for equip in equipment_list:
                print(f"      └── EQUIPMENT: {equip.name} [{equip.code}]")
                
                # Get sub-equipment
                sub_equip_list = Equipment.objects.filter(parent=equip)
                for sub_equip in sub_equip_list:
                    print(f"          └── SUB-EQUIPMENT: {sub_equip.name} [{sub_equip.code}]")
                    
                    # Get sub-sub-equipment
                    sub_sub_equip_list = Equipment.objects.filter(parent=sub_equip)
                    for sub_sub_equip in sub_sub_equip_list:
                        print(f"              └── SUB-SUB-EQUIPMENT: {sub_sub_equip.name} [{sub_sub_equip.code}]")
                
                # Get spare parts for this equipment
                relationships = BOMRelationship.objects.filter(
                    equipment=equip, 
                    spare_part__isnull=False
                )
                
                if relationships.exists():
                    print(f"          └── SPARE PARTS:")
                    for rel in relationships:
                        part = rel.spare_part
                        print(f"              └── {part.name} [{part.code}] - {part.category.name}")

if __name__ == "__main__":
    print_area_hierarchy()
    print_equipment_hierarchy()
    print_category_hierarchy()
    print_equipment_parts_relationships()
    print("\n")
    print_complete_hierarchy() 