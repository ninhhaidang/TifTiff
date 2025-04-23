#!/usr/bin/env python3
"""
Build script for packaging TifTiff application for Windows, macOS, and Linux
"""
import os
import sys
import platform
import subprocess
import shutil

def build_for_current_platform():
    """Build the application for the current operating system"""
    system = platform.system().lower()
    
    # Base command
    cmd = [
        'pyinstaller',
        '--name=TifTiff',
        '--windowed',  # GUI mode
        '--onefile',  # Single executable
        '--clean',  # Clean cache
    ]
    
    # Xử lý các tài nguyên
    if os.path.exists('resources'):
        # Điều chỉnh path separator tùy thuộc vào OS
        if system == 'windows':
            cmd.append('--add-data=resources;resources')
        else:
            cmd.append('--add-data=resources:resources')
    
    # Thêm icon nếu tồn tại
    if os.path.exists('icon.ico'):
        cmd.append('--icon=icon.ico')
    
    # Platform-specific adjustments
    if system == 'darwin':  # macOS
        print("Building for macOS...")
        # Add macOS specific options
        cmd.append('--osx-bundle-identifier=com.tiftiff.app')
        # Xác định kiến trúc - Intel hoặc Apple Silicon
        arch = platform.machine()
        if arch == 'arm64':
            print("Detected Apple Silicon (ARM64)")
            cmd.append('--target-architecture=arm64')
        elif arch == 'x86_64':
            print("Detected Intel (x86_64)")
            cmd.append('--target-architecture=x86_64')
        else:
            print(f"Unknown architecture: {arch}, using universal2")
            cmd.append('--target-architecture=universal2')
            
    elif system == 'windows':
        print("Building for Windows...")
        # Windows specific options
        if os.path.exists('version.txt'):
            cmd.append('--version-file=version.txt')
    elif system == 'linux':
        print("Building for Linux...")
        # Linux specific options if needed
    else:
        print(f"Unsupported platform: {system}")
        return False
    
    # Add main script
    cmd.append('app.py')
    
    # Run PyInstaller
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    
    if result.returncode != 0:
        print(f"Build failed with exit code {result.returncode}")
        return False
    
    print(f"Build completed for {system}")
    return True

def create_version_file():
    """Create a version file for Windows builds"""
    version = "1.0.0"  # You can get this from your config or another source
    
    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version.replace('.', ', ')}, 0),
    prodvers=({version.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'TifTiff'),
          StringStruct(u'FileDescription', u'TifTiff Image Processing Tool'),
          StringStruct(u'FileVersion', u'{version}'),
          StringStruct(u'InternalName', u'TifTiff'),
          StringStruct(u'LegalCopyright', u'© 2023 TifTiff'),
          StringStruct(u'OriginalFilename', u'TifTiff.exe'),
          StringStruct(u'ProductName', u'TifTiff'),
          StringStruct(u'ProductVersion', u'{version}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)""")
    return True

def main():
    """Main build function"""
    # Create build directory if it doesn't exist
    if not os.path.exists('build'):
        os.makedirs('build')
    
    # Create dist directory if it doesn't exist
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # For Windows builds, create a version file
    if platform.system().lower() == 'windows':
        create_version_file()
    
    # Build the application
    success = build_for_current_platform()
    
    if success:
        print("Build process completed successfully!")
        # Print location of the output file
        system = platform.system().lower()
        if system == 'windows':
            print(f"Executable can be found at: {os.path.abspath('dist/TifTiff.exe')}")
        elif system == 'darwin':
            print(f"Application can be found at: {os.path.abspath('dist/TifTiff.app')}")
        else:
            print(f"Executable can be found at: {os.path.abspath('dist/TifTiff')}")
    else:
        print("Build process failed.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 