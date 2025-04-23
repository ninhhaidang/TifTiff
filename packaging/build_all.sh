#!/bin/bash

# Script to build TifTiff for all supported platforms
# Usage: ./build_all.sh [mac|win|linux|all]

set -e

# Check for Python - sử dụng python3 thay vì python
if ! command -v python3 &> /dev/null; then
    echo "Python could not be found. Please install Python 3.8 or later."
    exit 1
fi

# Check for PyInstaller
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "PyInstaller could not be found. Installing..."
    pip3 install pyinstaller
fi

# Function to build for current platform
build_current() {
    echo "Building for current platform..."
    python3 build.py
    echo "Build completed!"
}

# Function to build for macOS (only works on macOS)
build_mac() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Building for macOS..."
        python3 build.py
        
        # Create DMG if create-dmg is installed
        if command -v create-dmg &> /dev/null; then
            echo "Creating DMG package..."
            # Create a directory for the DMG contents
            mkdir -p dmg_contents
            cp -r dist/TifTiff.app dmg_contents/
            
            create-dmg \
                --volname "TifTiff Installer" \
                --window-pos 200 120 \
                --window-size 800 400 \
                --icon-size 100 \
                --icon "TifTiff.app" 200 190 \
                --hide-extension "TifTiff.app" \
                --app-drop-link 600 185 \
                "TifTiff.dmg" \
                "dmg_contents/"
                
            echo "DMG created: TifTiff.dmg"
            rm -rf dmg_contents
        else
            echo "create-dmg not found. Skipping DMG creation."
            echo "To create a DMG, install create-dmg with 'brew install create-dmg'"
        fi
    else
        echo "Error: macOS build can only be performed on a Mac."
        echo "Consider using a macOS virtual machine or build service."
    fi
}

# Function to build for Windows
build_win() {
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
        # On Windows
        echo "Building for Windows..."
        python3 build.py
        
        # Create installer if Inno Setup CLI is available
        if command -v iscc &> /dev/null; then
            echo "Creating Windows installer..."
            mkdir -p installer
            iscc setup.iss
            echo "Installer created: installer/TifTiff_Setup.exe"
        else
            echo "Inno Setup CLI (iscc) not found. Skipping installer creation."
            echo "To create an installer, install Inno Setup and ensure iscc is in your PATH."
        fi
    else
        # On non-Windows platforms
        if command -v wine &> /dev/null; then
            echo "Building for Windows using Wine..."
            # Assume PyInstaller is installed in the Wine Python environment
            wine pyinstaller --name=TifTiff --windowed --onefile --clean --add-data="resources;resources" --icon=icon.ico app.py
            echo "Windows build completed using Wine!"
        else
            echo "Error: On non-Windows platforms, Wine is required to build for Windows."
            echo "Install Wine and set up a Windows Python environment in Wine."
        fi
    fi
}

# Function to build for Linux
build_linux() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # On Linux
        echo "Building for Linux..."
        python3 build.py
        
        # Create .deb package if fpm is available
        if command -v fpm &> /dev/null; then
            echo "Creating .deb package..."
            fpm -s dir -t deb -n tiftiff -v 1.0.0 \
                --prefix=/usr/local \
                dist/TifTiff=/usr/local/bin/ \
                resources/=/usr/local/share/tiftiff/resources/
            echo "DEB package created: tiftiff_1.0.0_amd64.deb"
        else
            echo "fpm not found. Skipping .deb package creation."
            echo "To create a .deb package, install fpm with 'gem install fpm'"
        fi
    else
        # On non-Linux platforms
        if command -v docker &> /dev/null; then
            echo "Building for Linux using Docker..."
            echo "Building Docker image..."
            docker build -t tiftiff-linux-build .
            
            echo "Running build in container..."
            docker run --name tiftiff-build tiftiff-linux-build
            
            echo "Copying build artifacts from container..."
            docker cp tiftiff-build:/app/dist ./dist-linux
            
            echo "Cleaning up..."
            docker rm tiftiff-build
            
            echo "Linux build completed! Results in ./dist-linux"
        else
            echo "Error: On non-Linux platforms, Docker is required to build for Linux."
            echo "Please install Docker to continue."
        fi
    fi
}

# Process command line arguments
if [ "$#" -eq 0 ]; then
    # No arguments, build for current platform
    build_current
else
    # Process specific build targets
    case $1 in
        mac|macos|darwin)
            build_mac
            ;;
        win|windows)
            build_win
            ;;
        linux)
            build_linux
            ;;
        all)
            echo "Building for all platforms..."
            build_mac
            build_win
            build_linux
            echo "All builds completed!"
            ;;
        *)
            echo "Unknown platform: $1"
            echo "Usage: ./build_all.sh [mac|win|linux|all]"
            exit 1
            ;;
    esac
fi

exit 0 