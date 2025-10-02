#!/usr/bin/env python3
"""
Simple ByteBouncer Test - Scan current directory to identify path issues
"""
import sys
import os
sys.path.append('.')

try:
    from app import ByteBouncerApp
    import tkinter as tk
    
    def test_scan():
        """Test scanning current directory"""
        print("Testing ByteBouncer scan functionality...")
        
        # Create app instance
        app_instance = ByteBouncerApp()
        
        # Test scan_directory method directly
        current_dir = os.getcwd()
        print(f"Scanning: {current_dir}")
        
        try:
            results = app_instance.scan_directory(current_dir, max_depth=1)
            
            print(f"\n📊 Scan Results:")
            print(f"  Files found: {len(results['files'])}")
            print(f"  Categories: {len(results['categories'])}")
            print(f"  Large files: {len(results['large_files'])}")
            
            # Show first few files
            print(f"\n📁 Sample files:")
            for i, file_info in enumerate(results['files'][:5]):
                print(f"  {i+1}. {file_info['name']}")
                print(f"     Path: {repr(file_info['path'])}")
                print(f"     Exists: {os.path.exists(file_info['path'])}")
                print(f"     Size: {file_info['size']} bytes")
                print()
            
            if len(results['files']) > 5:
                print(f"  ... and {len(results['files']) - 5} more files")
            
            # Test file operations on first file
            if results['files']:
                test_file = results['files'][0]
                print(f"\n🔧 Testing file operations on: {test_file['name']}")
                
                path = test_file['path']
                normalized_path = os.path.normpath(path)
                
                print(f"  Original path: {repr(path)}")
                print(f"  Normalized path: {repr(normalized_path)}")
                print(f"  Original exists: {os.path.exists(path)}")
                print(f"  Normalized exists: {os.path.exists(normalized_path)}")
                
                # Test safety check
                is_safe, msg = app_instance.is_safe_to_delete(path)
                print(f"  Safe to delete: {is_safe} - {msg}")
            
            return True
            
        except Exception as e:
            print(f"❌ Scan failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Clean up
            app_instance.destroy()
    
    if __name__ == "__main__":
        print("ByteBouncer Path Test")
        print("=" * 30)
        
        success = test_scan()
        
        if success:
            print("\n✅ Scan test completed successfully!")
            print("💡 If you're still having path issues:")
            print("   1. Run ByteBouncer normally: python app.py")
            print("   2. Scan a small folder (like current directory)")
            print("   3. Select a few files")
            print("   4. Use '🐛 Debug Paths' button to see exact path formats")
        else:
            print("\n❌ Scan test failed - check error messages above")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the ByteBouncer directory and dependencies are installed")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()