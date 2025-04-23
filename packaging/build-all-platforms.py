#!/usr/bin/env python3
"""
Đóng gói ứng dụng TifTiff cho Windows, macOS và Linux bằng PyInstaller
"""
import os
import sys
import platform
import subprocess
import shutil

def build_for_mac():
    """Đóng gói cho macOS"""
    print("===== Đóng gói cho macOS =====")
    result = subprocess.run(['pyinstaller', 'mac.spec'], check=False)
    if result.returncode == 0:
        print("✓ Build macOS thành công!")
        
        # Tạo DMG nếu có công cụ create-dmg
        if shutil.which('create-dmg'):
            print("Đang tạo file DMG...")
            try:
                if not os.path.exists('dmg_contents'):
                    os.makedirs('dmg_contents')
                
                # Copy .app vào thư mục tạm
                shutil.copytree('dist/TifTiff.app', 'dmg_contents/TifTiff.app', dirs_exist_ok=True)
                
                # Tạo DMG
                subprocess.run([
                    'create-dmg',
                    '--volname', 'TifTiff Installer',
                    '--window-pos', '200', '120',
                    '--window-size', '800', '400',
                    '--icon-size', '100',
                    '--icon', 'TifTiff.app', '200', '190',
                    '--hide-extension', 'TifTiff.app',
                    '--app-drop-link', '600', '185',
                    'TifTiff.dmg',
                    'dmg_contents/'
                ], check=False)
                
                # Dọn dẹp
                shutil.rmtree('dmg_contents', ignore_errors=True)
                print("✓ Tạo DMG thành công: TifTiff.dmg")
            except Exception as e:
                print(f"✗ Lỗi khi tạo DMG: {e}")
        else:
            print("! Không tìm thấy create-dmg. Bỏ qua bước tạo DMG.")
    else:
        print(f"✗ Build macOS thất bại với mã lỗi {result.returncode}")
    
    print()

def build_for_windows():
    """Đóng gói cho Windows"""
    print("===== Đóng gói cho Windows =====")
    
    # Trên macOS, không sử dụng Wine, chỉ tạo file spec
    if platform.system() == 'Darwin':
        print("Đang chạy trên macOS, tạo file spec cho Windows nhưng không build.")
        print("Để build cho Windows, hãy chạy lệnh sau trên máy Windows:")
        print("   pyinstaller win.spec")
        print("File spec đã được tạo: win.spec")
    else:
        result = subprocess.run(['pyinstaller', 'win.spec'], check=False)
        if result.returncode == 0:
            print("✓ Build Windows thành công!")
        else:
            print(f"✗ Build Windows thất bại với mã lỗi {result.returncode}")
    
    print()

def build_for_linux():
    """Đóng gói cho Linux"""
    print("===== Đóng gói cho Linux =====")
    
    # Nếu đang chạy trên macOS, sử dụng Docker
    if platform.system() == 'Darwin':
        if shutil.which('docker'):
            print("Đang sử dụng Docker để build Linux...")
            try:
                # Tạo và chạy container Docker
                print("Đang tạo Docker image...")
                subprocess.run(['docker', 'build', '-t', 'tiftiff-linux-build', '.'], check=True)
                
                print("Đang chạy container...")
                subprocess.run(['docker', 'run', '--name', 'tiftiff-build', 'tiftiff-linux-build'], check=True)
                
                # Tạo thư mục đích nếu chưa tồn tại
                if not os.path.exists('dist-linux'):
                    os.makedirs('dist-linux')
                
                # Copy kết quả từ container
                print("Đang copy kết quả từ container...")
                subprocess.run(['docker', 'cp', 'tiftiff-build:/app/dist/.', 'dist-linux/'], check=True)
                
                # Dọn dẹp
                print("Đang dọn dẹp...")
                subprocess.run(['docker', 'rm', 'tiftiff-build'], check=True)
                
                print("✓ Build Linux thành công! Kết quả trong ./dist-linux")
            except subprocess.CalledProcessError as e:
                print(f"✗ Lỗi khi build Linux: {e}")
            except Exception as e:
                print(f"✗ Lỗi không xác định: {e}")
        else:
            print("! Docker không được cài đặt. Không thể build cho Linux.")
            print("Để build cho Linux, hãy cài đặt Docker hoặc chạy trên máy Linux:")
            print("   pyinstaller linux.spec")
    else:
        # Nếu đang chạy trực tiếp trên Linux
        if platform.system() == 'Linux':
            result = subprocess.run(['pyinstaller', 'linux.spec'], check=False)
            if result.returncode == 0:
                print("✓ Build Linux thành công!")
            else:
                print(f"✗ Build Linux thất bại với mã lỗi {result.returncode}")
        else:
            print("! Đang chạy trên Windows. Không thể build trực tiếp cho Linux.")
    
    print()

def main():
    """Hàm chính"""
    # Kiểm tra Python và PyInstaller
    try:
        import PyInstaller
        print(f"Sử dụng PyInstaller phiên bản {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller chưa được cài đặt. Đang cài đặt...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    print(f"Đang chạy trên: {platform.system()} {platform.release()}")
    print(f"Python version: {platform.python_version()}")
    print()
    
    # Xử lý tham số dòng lệnh
    if len(sys.argv) > 1:
        platforms = [arg.lower() for arg in sys.argv[1:]]
    else:
        # Mặc định build cho tất cả
        platforms = ['mac', 'windows', 'linux']
    
    # Build cho các nền tảng được chỉ định
    for platform_name in platforms:
        if platform_name in ['mac', 'macos', 'darwin']:
            build_for_mac()
        elif platform_name in ['win', 'windows']:
            build_for_windows()
        elif platform_name in ['linux', 'unix']:
            build_for_linux()
        elif platform_name == 'all':
            build_for_mac()
            build_for_windows()
            build_for_linux()
        else:
            print(f"! Nền tảng không hỗ trợ: {platform_name}")
    
    print("Quá trình đóng gói hoàn tất!")

if __name__ == "__main__":
    main() 