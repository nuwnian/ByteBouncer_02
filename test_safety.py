#!/usr/bin/env python3
"""
Test script to demonstrate ByteBouncer's enhanced safety features
"""

import os
import tempfile
from pathlib import Path

# Create test files to demonstrate safety warnings
def create_test_files():
    """Create various test files to show safety categorization"""
    
    test_dir = Path("test_safety_files")
    test_dir.mkdir(exist_ok=True)
    
    # Safe files
    (test_dir / "photo.jpg").write_bytes(b"fake image data" * 1000)
    (test_dir / "music.mp3").write_bytes(b"fake audio data" * 500)
    (test_dir / "temp_data.txt").write_text("Temporary text file content")
    
    # Caution files (large)
    large_content = b"Large file content " * 1024 * 1024  # ~20MB
    (test_dir / "large_video.mp4").write_bytes(large_content)
    
    # Dangerous files (important)
    (test_dir / "important_config.ini").write_text("[Settings]\nkey=value")
    (test_dir / "system_backup.dll").write_bytes(b"fake dll data")
    (test_dir / "project.sln").write_text("Microsoft Visual Studio Solution File")
    (test_dir / "database.db").write_bytes(b"fake database content")
    
    print("✅ Test files created in 'test_safety_files' folder:")
    print("🟢 Safe files: photo.jpg, music.mp3, temp_data.txt")
    print("🟡 Caution files: large_video.mp4 (large file)")
    print("🔴 Dangerous files: important_config.ini, system_backup.dll, project.sln, database.db")
    print("\nNow run ByteBouncer and scan this folder to see safety warnings!")

if __name__ == "__main__":
    create_test_files()