"""
Script to clean up migrations and fix migration issues
"""
import os
import glob
import re
import sys
import django
import shutil

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSBDM.settings')
django.setup()

def find_migration_references():
    """Find all files that might reference migrations"""
    pattern = r"dependencies.*?[\'\"]([a-zA-Z_]+)[\'\"],\s*[\'\"]([0-9_]+).*?[\'\"]"
    
    for dirpath, dirnames, filenames in os.walk('.'):
        if '__pycache__' in dirpath:
            continue
            
        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"Found migration references in {filepath}:")
                            for app, migration in matches:
                                print(f"  - {app}.{migration}")
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")

def clean_migrations():
    """Clean up migration files and directories"""
    # Find all migration directories
    migration_dirs = []
    for app_dir in ['equipment', 'spare_parts', 'documents', 'ssbom', 'maintenance', 'security']:
        migration_dir = os.path.join(app_dir, 'migrations')
        if os.path.exists(migration_dir):
            migration_dirs.append(migration_dir)
    
    # Clean each directory
    for migration_dir in migration_dirs:
        print(f"Cleaning directory: {migration_dir}")
        
        # Keep __init__.py
        for file in os.listdir(migration_dir):
            if file != '__init__.py' and file.endswith('.py'):
                file_path = os.path.join(migration_dir, file)
                try:
                    os.remove(file_path)
                    print(f"  - Removed: {file_path}")
                except Exception as e:
                    print(f"  - Error removing {file_path}: {e}")
        
        # Remove __pycache__ directory
        pycache_dir = os.path.join(migration_dir, '__pycache__')
        if os.path.exists(pycache_dir):
            try:
                shutil.rmtree(pycache_dir)
                print(f"  - Removed: {pycache_dir}")
            except Exception as e:
                print(f"  - Error removing {pycache_dir}: {e}")

if __name__ == "__main__":
    print("Finding migration references...")
    find_migration_references()
    
    print("\nCleaning migrations...")
    clean_migrations()
    
    print("\nDone!") 