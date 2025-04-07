#!/usr/bin/env python
import os
import sys
import codecs

def find_encoding_issues(directory, extensions=('.py',), verbose=True):
    """Find files with encoding issues (null bytes, BOM, invalid UTF-8)."""
    problematic_files = []
    file_count = 0
    
    if verbose:
        print(f"Scanning directory: {directory}")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                file_count += 1
                try:
                    # First check for BOM
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        issues = []
                        
                        # Check for BOM
                        if content.startswith(codecs.BOM_UTF8):
                            issues.append("BOM")
                        
                        # Check for null bytes
                        if b'\x00' in content:
                            issues.append(f"{content.count(b'\x00')} null bytes")
                        
                        # Try to decode as UTF-8
                        try:
                            content.decode('utf-8')
                        except UnicodeDecodeError as e:
                            issues.append(f"Invalid UTF-8: {str(e)}")
                        
                        if issues:
                            problematic_files.append((file_path, issues))
                            if verbose:
                                print(f"Found issues in: {file_path} ({', '.join(issues)})")
                            
                except Exception as e:
                    if verbose:
                        print(f"Error reading {file_path}: {e}")
    
    if verbose:
        print(f"Scanned {file_count} files.")
    
    return problematic_files

def fix_file(file_path, verbose=True):
    """Fix encoding issues in a file."""
    try:
        # Read the file in binary mode
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Remove BOM if present
        if content.startswith(codecs.BOM_UTF8):
            content = content[len(codecs.BOM_UTF8):]
        
        # Remove null bytes
        content = content.replace(b'\x00', b'')
        
        # Try to decode as UTF-8
        try:
            decoded_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # If we can't decode as UTF-8, try to fix it
            decoded_content = content.decode('utf-8', errors='replace')
        
        # Write the cleaned content back
        with open(file_path, 'wb') as f:
            f.write(decoded_content.encode('utf-8'))
        
        if verbose:
            print(f"Fixed: {file_path}")
        
        return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        directory = "."  # Default to current directory
    else:
        directory = sys.argv[1]
    
    print(f"Scanning for files with encoding issues in {directory}...")
    problematic_files = find_encoding_issues(directory)
    
    if not problematic_files:
        print("No files with encoding issues found.")
        return
    
    print(f"\nFound {len(problematic_files)} files with encoding issues:")
    for file_path, issues in problematic_files:
        print(f"  - {file_path} ({', '.join(issues)})")
    
    print("\nFixing all files automatically...")
    fixed_count = 0
    for file_path, _ in problematic_files:
        if fix_file(file_path):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} out of {len(problematic_files)} files.")

if __name__ == "__main__":
    main() 