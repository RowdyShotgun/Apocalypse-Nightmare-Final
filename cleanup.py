#!/usr/bin/env python3
"""
Cleanup script for the text adventure game.
Identifies and fixes various code quality issues.
"""

import os
import re
import sys

def cleanup_file(filepath):
    """Clean up a single file by removing unnecessary code and improving formatting."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Remove empty pass statements
    content = re.sub(r'except Exception as e:\s*#.*\s*pass\s*', 
                    'except Exception as e:\n                # Silently handle any errors\n                continue\n', 
                    content)
    
    # 2. Remove standalone pass statements
    content = re.sub(r'^\s*pass\s*$', '', content, flags=re.MULTILINE)
    
    # 3. Clean up excessive blank lines (more than 2 consecutive)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 4. Remove trailing whitespace
    content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
    
    # 5. Ensure consistent indentation (4 spaces)
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip():  # Non-empty line
            # Count leading spaces
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 0:
                # Convert to 4-space indentation
                indent_level = leading_spaces // 4
                cleaned_line = '    ' * indent_level + line.lstrip()
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        else:
            cleaned_lines.append('')
    
    content = '\n'.join(cleaned_lines)
    
    # Only write if content changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def find_unused_imports(filepath):
    """Find potentially unused imports in a file."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all import statements
    import_pattern = r'^(?:from\s+(\w+)\s+import\s+([^#\n]+)|import\s+([^#\n]+))'
    imports = re.findall(import_pattern, content, re.MULTILINE)
    
    # Find all function calls and variable uses
    function_pattern = r'\b(\w+)\s*\('
    variable_pattern = r'\b(\w+)\s*[=+\-*/<>!]'
    
    functions = re.findall(function_pattern, content)
    variables = re.findall(variable_pattern, content)
    
    all_uses = set(functions + variables)
    
    unused_imports = []
    for import_match in imports:
        if import_match[0]:  # from ... import ...
            module = import_match[0]
            items = [item.strip() for item in import_match[1].split(',')]
            for item in items:
                if item not in all_uses:
                    unused_imports.append(f"from {module} import {item}")
        elif import_match[2]:  # import ...
            module = import_match[2].strip()
            if module not in all_uses:
                unused_imports.append(f"import {module}")
    
    return unused_imports

def analyze_code_quality():
    """Analyze overall code quality and provide recommendations."""
    
    print("🔍 Analyzing Code Quality...")
    print("=" * 50)
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    
    total_issues = 0
    total_files = 0
    
    for filename in python_files:
        print(f"\n📄 {filename}:")
        
        # Check for unused imports
        unused_imports = find_unused_imports(filename)
        if unused_imports:
            print(f"  ⚠️  Potentially unused imports:")
            for imp in unused_imports:
                print(f"     - {imp}")
            total_issues += len(unused_imports)
        
        # Check for long functions (more than 50 lines)
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        long_functions = []
        current_function = None
        function_start = 0
        
        for i, line in enumerate(lines):
            if re.match(r'^\s*def\s+\w+', line):
                if current_function and (i - function_start) > 50:
                    long_functions.append((current_function, i - function_start))
                current_function = line.strip().split('def ')[1].split('(')[0]
                function_start = i
        
        # Check last function
        if current_function and (len(lines) - function_start) > 50:
            long_functions.append((current_function, len(lines) - function_start))
        
        if long_functions:
            print(f"  📏 Long functions (>50 lines):")
            for func_name, line_count in long_functions:
                print(f"     - {func_name}: {line_count} lines")
            total_issues += len(long_functions)
        
        # Check for hardcoded strings
        hardcoded_strings = []
        for i, line in enumerate(lines):
            if '"' in line or "'" in line:
                # Simple check for hardcoded strings (could be improved)
                if len(line.strip()) > 100 and ('"' in line or "'" in line):
                    hardcoded_strings.append(i + 1)
        
        if hardcoded_strings:
            print(f"  📝 Long hardcoded strings on lines: {hardcoded_strings[:5]}")
            total_issues += len(hardcoded_strings)
        
        total_files += 1
    
    print(f"\n📊 Summary:")
    print(f"  Files analyzed: {total_files}")
    print(f"  Total issues found: {total_issues}")
    
    if total_issues == 0:
        print("  ✅ Code quality looks good!")
    else:
        print("  🔧 Consider addressing the issues above for better code quality.")

def cleanup_all_files():
    """Clean up all Python files in the current directory."""
    
    print("🧹 Starting Code Cleanup...")
    print("=" * 50)
    
    python_files = [f for f in os.listdir('.') if f.endswith('.py')]
    cleaned_files = 0
    
    for filename in python_files:
        print(f"Cleaning {filename}...")
        if cleanup_file(filename):
            cleaned_files += 1
            print(f"  ✅ {filename} cleaned")
        else:
            print(f"  ℹ️  {filename} already clean")
    
    print(f"\n🎉 Cleanup complete! {cleaned_files} files were modified.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        analyze_code_quality()
    else:
        cleanup_all_files()
        print("\n" + "=" * 50)
        analyze_code_quality() 