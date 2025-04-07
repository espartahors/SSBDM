from django.core.management.base import BaseCommand
from maintenance.models import Area, Equipment
import csv
import os
from django.db import transaction

class Command(BaseCommand):
    help = 'Import equipment/area hierarchy from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('--delimiter', type=str, default=';', help='CSV delimiter (default: ;)')
        parser.add_argument('--dry-run', action='store_true', help='Run without making changes to the database')
        parser.add_argument('--verbose', action='store_true', help='Show verbose output')

    def handle(self, *args, **options):
        file_path = options['csv_file']
        delimiter = options['delimiter']
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Starting import from {file_path}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No database changes will be made'))
        
        self.stdout.write(f"Before import - Areas count: {Area.objects.count()}")
        self.stdout.write(f"Before import - Equipment count: {Equipment.objects.count()}")
        
        # Dictionary to store created areas for reference
        area_cache = {}
        equipment_cache = {}
        created_count = {'area': 0, 'equipment': 0}
        skipped_count = 0
        
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=delimiter)
            
            # Skip header if it exists
            first_row = next(reader, None)
            if first_row and 'LEVEL' in str(first_row):
                self.stdout.write(f"Skipping header: {first_row}")
            else:
                # If it wasn't a header, reposition to start
                csv_file.seek(0)
                reader = csv.reader(csv_file, delimiter=delimiter)
                
            all_rows = list(reader)
        
        try:
            with transaction.atomic():
                # First, create all areas (level 1 and 2)
                for i, row in enumerate(all_rows, 1):
                    if not row or not any(row):
                        continue
                    
                    # Extract fields
                    level = str(row[0]).strip() if len(row) > 0 else None
                    l1_code = str(row[1]).strip() if len(row) > 1 and row[1] else None
                    l2_code = str(row[2]).strip() if len(row) > 2 and row[2] else None
                    
                    # Get description from column 6
                    description = str(row[6]).strip() if len(row) > 6 and row[6] else None
                    
                    if verbose:
                        self.stdout.write(f"Processing row {i}: Level={level}, L1={l1_code}, L2={l2_code}, Desc={description}")
                    
                    # Process Level 1 - Primary Areas
                    if level == '1' and l1_code:
                        name = description or f"Area {l1_code}"
                        
                        if not dry_run:
                            area, created = Area.objects.get_or_create(
                                code=l1_code,
                                defaults={'name': name, 'description': description}
                            )
                            area_cache[l1_code] = area
                            if created:
                                created_count['area'] += 1
                            action = "Created" if created else "Found existing"
                            self.stdout.write(self.style.SUCCESS(f"{action} Area: {l1_code} - {name}"))
                        else:
                            self.stdout.write(f"Would create Area: {l1_code} - {name}")
                    
                    # Process Level 2 - Sub-Areas
                    if level == '2' and l1_code and l2_code:
                        name = description or f"Sub-area {l2_code}"
                        
                        # First ensure parent area exists
                        if l1_code not in area_cache and not dry_run:
                            # Create parent if it doesn't exist
                            parent_area, created = Area.objects.get_or_create(
                                code=l1_code,
                                defaults={'name': f"Area {l1_code}"}
                            )
                            area_cache[l1_code] = parent_area
                            if created:
                                created_count['area'] += 1
                                self.stdout.write(self.style.SUCCESS(f"Created parent Area: {l1_code}"))
                        
                        if not dry_run:
                            parent = area_cache.get(l1_code)
                            if parent:
                                area, created = Area.objects.get_or_create(
                                    code=l2_code,
                                    defaults={
                                        'name': name,
                                        'description': description,
                                        'parent': parent
                                    }
                                )
                                area_cache[l2_code] = area
                                if created:
                                    created_count['area'] += 1
                                action = "Created" if created else "Found existing"
                                self.stdout.write(self.style.SUCCESS(f"{action} Sub-area: {l2_code} - {name} (parent: {l1_code})"))
                            else:
                                self.stderr.write(self.style.WARNING(f"Parent area {l1_code} not available"))
                        else:
                            self.stdout.write(f"Would create Sub-area: {l2_code} - {name} (parent: {l1_code})")
                
                # Second pass for equipment (level 3 and 4)
                for i, row in enumerate(all_rows, 1):
                    if not row or not any(row):
                        continue
                    
                    # Extract fields
                    level = str(row[0]).strip() if len(row) > 0 else None
                    l1_code = str(row[1]).strip() if len(row) > 1 and row[1] else None
                    l2_code = str(row[2]).strip() if len(row) > 2 and row[2] else None
                    l3_code = str(row[3]).strip() if len(row) > 3 and row[3] else None
                    l4_code = str(row[4]).strip() if len(row) > 4 and row[4] else None
                    l5_code = str(row[5]).strip() if len(row) > 5 and row[5] else None
                    
                    # Get description from column 6
                    description = str(row[6]).strip() if len(row) > 6 and row[6] else None
                    
                    # Process Level 3 - Main Equipment
                    if level == '3' and l1_code and l2_code and l3_code:
                        name = description or f"Equipment {l3_code}"
                        
                        # Make sure parent area exists
                        if l2_code not in area_cache and not dry_run:
                            if l1_code in area_cache:
                                # Create the area if needed
                                parent_area, created = Area.objects.get_or_create(
                                    code=l2_code,
                                    defaults={
                                        'name': f"Area {l2_code}",
                                        'parent': area_cache[l1_code]
                                    }
                                )
                                area_cache[l2_code] = parent_area
                                if created:
                                    created_count['area'] += 1
                                    self.stdout.write(self.style.SUCCESS(f"Created parent Area: {l2_code}"))
                        
                        if not dry_run and l2_code in area_cache:
                            equipment, created = Equipment.objects.get_or_create(
                                code=l3_code,
                                defaults={
                                    'name': name,
                                    'description': description,
                                    'equipment_type': 'System',
                                    'area': area_cache[l2_code],
                                    'status': 'operational'
                                }
                            )
                            equipment_cache[l3_code] = equipment
                            if created:
                                created_count['equipment'] += 1
                            action = "Created" if created else "Found existing"
                            self.stdout.write(self.style.SUCCESS(f"{action} Equipment: {l3_code} - {name} (area: {l2_code})"))
                        else:
                            self.stdout.write(f"Would create Equipment: {l3_code} - {name} (area: {l2_code})")
                    
                    # Process Level 4 - Components
                    if level == '4' and l1_code and l2_code and l3_code and l4_code:
                        # If column 5 has a value, use it as part of the name
                        if l5_code:
                            name = f"{l5_code} - {description}" if description else f"{l5_code}"
                        else:
                            name = description or f"Component {l4_code}"
                        
                        # Make sure parent equipment exists
                        if l3_code not in equipment_cache and not dry_run:
                            # Try to find parent equipment in database
                            try:
                                parent_eq = Equipment.objects.get(code=l3_code)
                                equipment_cache[l3_code] = parent_eq
                            except Equipment.DoesNotExist:
                                # Create the parent equipment if it doesn't exist
                                if l2_code in area_cache:
                                    parent_eq = Equipment.objects.create(
                                        code=l3_code,
                                        name=f"Equipment {l3_code}",
                                        equipment_type='System',
                                        area=area_cache[l2_code],
                                        status='operational'
                                    )
                                    equipment_cache[l3_code] = parent_eq
                                    created_count['equipment'] += 1
                                    self.stdout.write(self.style.SUCCESS(f"Created parent Equipment: {l3_code}"))
                        
                        if not dry_run and l3_code in equipment_cache:
                            parent_eq = equipment_cache[l3_code]
                            component_code = f"{l3_code}-{l4_code}" if l5_code else l4_code
                            
                            component, created = Equipment.objects.get_or_create(
                                code=component_code,
                                defaults={
                                    'name': name,
                                    'description': description,
                                    'equipment_type': 'Component',
                                    'area': parent_eq.area,
                                    'parent': parent_eq,
                                    'status': 'operational'
                                }
                            )
                            if created:
                                created_count['equipment'] += 1
                            action = "Created" if created else "Found existing"
                            self.stdout.write(self.style.SUCCESS(f"{action} Component: {component_code} - {name} (parent: {l3_code})"))
                        else:
                            self.stdout.write(f"Would create Component: {l4_code} - {name} (parent: {l3_code})")
                
                if dry_run:
                    # If in dry run mode, roll back the transaction
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.SUCCESS('Dry run completed, no changes made to database'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Import completed - Created {created_count["area"]} areas and {created_count["equipment"]} equipment items'))
        
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Import failed: {str(e)}'))
            import traceback
            self.stderr.write(self.style.ERROR(traceback.format_exc()))
        
        self.stdout.write(f"After import - Areas count: {Area.objects.count()}")
        self.stdout.write(f"After import - Equipment count: {Equipment.objects.count()}")
        self.stdout.write(f"Skipped rows: {skipped_count}")