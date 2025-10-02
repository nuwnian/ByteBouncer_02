#!/usr/bin/env python3
"""
ByteBouncer Feature Showcase
Demonstrates all the capabilities of the enhanced disk analyzer
"""
import os
import sys
from pathlib import Path

def create_test_files():
    """Create sample files for testing features"""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create various file types
    files_to_create = [
        ("document.pdf", b"Sample PDF content" * 100),
        ("image.jpg", b"JPEG data" * 50),
        ("video.mp4", b"Video data" * 1000),
        ("audio.mp3", b"Audio data" * 200),
        ("code.py", b"print('Hello World')" * 10),
        ("archive.zip", b"ZIP archive" * 300),
        ("large_file.bin", b"Large binary data" * 50000),  # ~600KB
        # Duplicate files
        ("duplicate1.txt", b"This is duplicate content"),
        ("duplicate2.txt", b"This is duplicate content"),
        ("subfolder/duplicate3.txt", b"This is duplicate content"),
    ]
    
    print("Creating test files...")
    for filename, content in files_to_create:
        filepath = test_dir / filename
        filepath.parent.mkdir(exist_ok=True)
        filepath.write_bytes(content)
    
    print(f"✓ Created {len(files_to_create)} test files in {test_dir}/")
    return str(test_dir.absolute())

def display_features():
    """Display ByteBouncer features"""
    print("\n" + "="*60)
    print("🚀 BYTEBOUNCER - ENHANCED DISK SPACE ANALYZER")
    print("="*60)
    
    features = [
        "📊 Smart File Categorization",
        "🔍 Recursive Directory Scanning", 
        "💾 Real-time Drive Usage Monitoring",
        "🗂️ Interactive File Browser with Selection",
        "🔍 Advanced Duplicate File Detection",
        "🗑️ Safe File Deletion (Recycle Bin)",
        "📂 Quick File Location Access",
        "🧹 Intelligent Cleanup Recommendations",
        "⚙️ Persistent Configuration Settings",
        "📈 Space Usage Analysis & Reports"
    ]
    
    print("\n🎯 KEY FEATURES:")
    for i, feature in enumerate(features, 1):
        print(f"  {i:2d}. {feature}")
    
    print(f"\n📋 NEW FILE MANAGEMENT CAPABILITIES:")
    print(f"  • Select multiple files with checkboxes")
    print(f"  • Batch delete operations")
    print(f"  • MD5-based duplicate detection")
    print(f"  • Windows Explorer integration")
    print(f"  • Safe file operations with undo")
    
    print(f"\n🛡️ SAFETY FEATURES:")
    print(f"  • Files moved to Recycle Bin (not permanently deleted)")
    print(f"  • Confirmation dialogs for all operations")
    print(f"  • Error handling and recovery")
    print(f"  • Permission-aware scanning")

def main():
    """Main showcase function"""
    print("ByteBouncer Enhanced - Feature Showcase")
    print("="*50)
    
    # Display features
    display_features()
    
    # Offer to create test files
    print(f"\n📁 TEST ENVIRONMENT:")
    if input("Create test files for demonstration? (y/n): ").lower().startswith('y'):
        test_path = create_test_files()
        print(f"\n✅ Test files created at: {test_path}")
        print("   You can now scan this folder to test all features!")
    
    print(f"\n🚀 GETTING STARTED:")
    print(f"   1. Run: python app.py")
    print(f"   2. Click 'Browse' to select a folder")
    print(f"   3. Adjust scan depth (1-5 levels)")
    print(f"   4. Click '🔍 Start Scan'")
    print(f"   5. Explore the results in different tabs")
    
    print(f"\n💡 PRO TIPS:")
    print(f"   • Use File Browser tab to select and manage files")
    print(f"   • Try the Duplicates tab to find wasted space")
    print(f"   • Check Cleanup tab for large file recommendations")
    print(f"   • Double-click files to open their location")
    
    print(f"\n🔧 DEPENDENCIES INSTALLED:")
    try:
        import customtkinter
        print(f"   ✅ customtkinter {customtkinter.__version__}")
    except ImportError:
        print(f"   ❌ customtkinter (run: pip install customtkinter)")
    
    try:
        import psutil
        print(f"   ✅ psutil {psutil.__version__}")
    except ImportError:
        print(f"   ❌ psutil (run: pip install psutil)")
    
    try:
        import send2trash
        print(f"   ✅ send2trash (safe file deletion)")
    except ImportError:
        print(f"   ❌ send2trash (run: pip install send2trash)")
    
    print(f"\n🎉 Your ByteBouncer is ready to use!")
    print(f"   Run 'python app.py' to start the application.")

if __name__ == "__main__":
    main()