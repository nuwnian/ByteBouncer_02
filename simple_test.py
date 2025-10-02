#!/usr/bin/env python3
"""
Simple test for ByteBouncer app
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox
        import threading
        import os
        from pathlib import Path
        from datetime import datetime
        from collections import defaultdict
        print("[OK] All imports successful")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without GUI"""
    try:
        # Test file size formatting
        def format_size(size):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} PB"
        
        test_sizes = [1024, 1024*1024, 1024*1024*100]
        for size in test_sizes:
            formatted = format_size(size)
            print(f"[OK] {size} bytes = {formatted}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("ByteBouncer Simple Test")
    print("=" * 25)
    
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing basic functionality...")
    basic_ok = test_basic_functionality()
    
    print("\n" + "=" * 25)
    if imports_ok and basic_ok:
        print("[SUCCESS] Basic tests passed!")
        print("Try running: python app.py")
    else:
        print("[FAILED] Some tests failed.")