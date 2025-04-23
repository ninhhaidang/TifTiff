# Đóng gói ứng dụng TifTiff

Thư mục này chứa các công cụ và hướng dẫn để đóng gói ứng dụng TifTiff cho các hệ điều hành Windows, macOS và Linux.

## Cấu trúc thư mục

```
packaging/
├── build-all-platforms.py  # Script đóng gói cho tất cả các nền tảng
├── build_all.sh            # Script bash đóng gói (phiên bản cũ)
├── build.py                # Script Python đóng gói cơ bản
├── Dockerfile              # Cấu hình Docker để build cho Linux
├── linux.spec              # Cấu hình PyInstaller cho Linux
├── mac.spec                # Cấu hình PyInstaller cho macOS
├── output/                 # Thư mục chứa các bản build
│   └── TifTiff.dmg         # Bản đóng gói macOS
├── setup.iss               # Script Inno Setup cho Windows
├── TifTiff.spec            # Cấu hình PyInstaller chung
└── win.spec                # Cấu hình PyInstaller cho Windows
```

## Hướng dẫn sử dụng

### Cách đơn giản nhất

Sử dụng script `build-all-platforms.py` để đóng gói cho tất cả hoặc một nền tảng cụ thể:

```bash
# Đóng gói cho tất cả các nền tảng
python3 packaging/build-all-platforms.py

# Đóng gói cho macOS
python3 packaging/build-all-platforms.py mac

# Tạo file cấu hình cho Windows (cần build trên Windows)
python3 packaging/build-all-platforms.py win

# Đóng gói cho Linux (sử dụng Docker)
python3 packaging/build-all-platforms.py linux
```

### Sử dụng file cấu hình PyInstaller trực tiếp

Bạn có thể sử dụng file `.spec` để đóng gói trực tiếp:

```bash
# Đóng gói cho macOS
pyinstaller packaging/mac.spec

# Đóng gói cho Windows (chạy trên máy Windows)
pyinstaller packaging/win.spec

# Đóng gói cho Linux (chạy trên máy Linux)
pyinstaller packaging/linux.spec
```

## Đóng gói cho Windows từ macOS/Linux

Để đóng gói cho Windows từ macOS hoặc Linux, bạn có 2 lựa chọn:

1. Sử dụng Wine (không khuyến nghị vì có thể gặp lỗi):
   ```bash
   ./packaging/build_all.sh win
   ```

2. **Cách tốt nhất**: Copy file `win.spec` sang máy Windows và chạy:
   ```bash
   # Trên Windows
   pyinstaller win.spec
   ```

## Đóng gói cho Linux từ macOS/Windows

Sử dụng Docker để đóng gói cho Linux:

```bash
# Đảm bảo Docker đã được khởi động
open -a Docker

# Đóng gói cho Linux
python3 packaging/build-all-platforms.py linux
```

## Tạo file cài đặt

### macOS (DMG)

File DMG sẽ được tự động tạo nếu công cụ `create-dmg` được cài đặt. Kết quả sẽ được lưu tại `packaging/output/TifTiff.dmg`.

### Windows (EXE Installer)

Trên Windows, sử dụng Inno Setup với file `setup.iss`:

```bash
iscc setup.iss
```

Kết quả là file `installer/TifTiff_Setup.exe`.

### Linux (DEB/RPM)

Để tạo gói cài đặt cho Linux, sử dụng fpm:

```bash
# Tạo gói .deb (Debian/Ubuntu)
fpm -s dir -t deb -n tiftiff -v 1.0.0 \
  --prefix=/usr/local \
  dist/TifTiff=/usr/local/bin/ \
  resources/=/usr/local/share/tiftiff/resources/
```

## Thông tin thêm

Xem file [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) để biết thêm chi tiết. 