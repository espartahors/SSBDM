#!/usr/bin/env python
import os
import sys

def find_null_bytes(directory, extensions=('.py',)):
    """Find files with null bytes in them."""
    problematic_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        if b'\x00' in content:
                            problematic_files.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return problematic_files

def fix_file(file_path):
    """Remove null bytes from a file and save a cleaned version."""
    try:
        # Read the file in binary mode
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Remove null bytes
        cleaned_content = content.replace(b'\x00', b'')
        
        # Write the cleaned content back
        with open(file_path, 'wb') as f:
            f.write(cleaned_content)
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_null_bytes.py <directory>")
        print("Example: python fix_null_bytes.py .")
        return
    
    directory = sys.argv[1]
    problematic_files = find_null_bytes(directory)
    
    if not problematic_files:
        print("No files with null bytes found.")
        return
    
    print(f"Found {len(problematic_files)} files with null bytes:")
    for file in problematic_files:
        print(f"  - {file}")
    
    fix_all = input("\nFix all files? (y/n): ").lower() == 'y'
    
    if fix_all:
        fixed_count = 0
        for file in problematic_files:
            if fix_file(file):
                fixed_count += 1
                print(f"Fixed: {file}")
        
        print(f"\nFixed {fixed_count} out of {len(problematic_files)} files.")
    else:
        print("No files were modified.")

if __name__ == "__main__":
    main() 