#!/usr/bin/env python3
"""
ByteBouncer Path Diagnostics
Test file path handling and identify issues
"""
import os
import sys
from pathlib import Path

def test_path_handling():
    """Test various path scenarios"""
    print("ByteBouncer Path Diagnostics")
    print("=" * 40)
    
    # Test current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Test sample file paths
    test_paths = [
        "C:\\Windows\\System32\\notepad.exe",
        "C:/Windows/System32/notepad.exe",
        "D:\\ByteBouncer_02\\app.py",
        "D:/ByteBouncer_02/app.py",
        "..\\app.py",
        "../app.py"
    ]
    
    print(f"\n📁 Path Normalization Tests:")
    for path in test_paths:
        normalized = os.path.normpath(path)
        exists = os.path.exists(normalized)
        print(f"  Original: {path}")
        print(f"  Normalized: {normalized}")
        print(f"  Exists: {exists}")
        print()
    
    # Test os.scandir behavior
    print(f"📂 Testing os.scandir path format:")
    try:
        with os.scandir('.') as entries:
            for i, entry in enumerate(entries):
                if i >= 3:  # Just test first 3 entries
                    break
                print(f"  Entry: {entry.name}")
                print(f"  Path: {entry.path}")
                print(f"  Normalized: {os.path.normpath(entry.path)}")
                print(f"  Exists: {os.path.exists(entry.path)}")
                print()
    except Exception as e:
        print(f"  Error scanning directory: {e}")
    
    # Test file operations
    print(f"🔧 Testing file operations:")
    test_file = "app.py"
    if os.path.exists(test_file):
        try:
            stat = os.stat(test_file)
            print(f"  ✅ os.stat() works on {test_file}")
            print(f"  Size: {stat.st_size} bytes")
        except Exception as e:
            print(f"  ❌ os.stat() failed: {e}")
        
        try:
            with open(test_file, 'rb') as f:
                data = f.read(100)
            print(f"  ✅ File opening works")
        except Exception as e:
            print(f"  ❌ File opening failed: {e}")
    else:
        print(f"  ⚠️ Test file {test_file} not found")

def test_windows_paths():
    """Test Windows-specific path issues"""
    print(f"\n🪟 Windows Path Tests:")
    
    # Test common problematic paths
    problematic_paths = [
        "C:\\Windows\\Installer\\{12345678-1234-1234-1234-123456789012}\\",
        "C:\\Users\\User\\AppData\\Local\\Temp\\tmp1234.tmp",
        "C:\\Program Files (x86)\\Some App\\file.exe"
    ]
    
    for path in problematic_paths:
        normalized = os.path.normpath(path)
        print(f"  Path: {path}")
        print(f"  Normalized: {normalized}")
        print(f"  Directory exists: {os.path.exists(os.path.dirname(normalized))}")
        print()

def main():
    """Main diagnostics function"""
    test_path_handling()
    test_windows_paths()
    
    print("\n💡 Recommendations:")
    print("  1. Always use os.path.normpath() on file paths")
    print("  2. Check os.path.exists() before file operations")
    print("  3. Handle PermissionError and OSError exceptions")
    print("  4. Use raw strings or forward slashes for Windows paths")
    
    print("\n🎯 For ByteBouncer:")
    if os.path.exists("app.py"):
        print("  ✅ ByteBouncer app.py found - ready to test")
        print("  💡 Try scanning a small folder first (like current directory)")
        print("  💡 Use the new '🐛 Debug Paths' button to check file paths")
    else:
        print("  ❌ ByteBouncer app.py not found in current directory")

if __name__ == "__main__":
    main()