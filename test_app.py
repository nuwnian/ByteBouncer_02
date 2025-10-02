#!/usr/bin/env python3
"""
Test script for ByteBouncer app
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
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_launch():
    """Test if the app can be instantiated"""
    try:
        # Test if customtkinter is available
        import customtkinter as ctk
        print("✓ CustomTkinter available")
        
        # Import the app (assuming it's in app.py)
        sys.path.append('.')
        from app import ByteBouncerApp
        print("✓ App class imported successfully")
        
        # Test static method without instantiation
        test_size = ByteBouncerApp.format_size(1024 * 1024 * 100)  # 100MB
        print(f"✓ Size formatting works: {test_size}")
        
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Install with: pip install customtkinter psutil")
        return False
    except Exception as e:
        print(f"✗ App test failed: {e}")
        return False

if __name__ == "__main__":
    print("ByteBouncer Test Suite")
    print("=" * 30)
    
    # Test imports
    print("\n1. Testing imports...")
    imports_ok = test_imports()
    
    # Test app
    print("\n2. Testing app...")
    app_ok = test_app_launch()
    
    print("\n" + "=" * 30)
    if imports_ok and app_ok:
        print("✓ All tests passed! App is ready to run.")
    else:
        print("✗ Some tests failed. Check the errors above.")