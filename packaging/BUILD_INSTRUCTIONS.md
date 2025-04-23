# Hướng dẫn đóng gói TifTiff

Tài liệu này hướng dẫn cách đóng gói ứng dụng TifTiff cho các hệ điều hành Windows, macOS và Linux.

## Yêu cầu chung

Đảm bảo bạn đã cài đặt:

1. Python 3.8 trở lên
2. Các thư viện trong file `requirements.txt`
3. PyInstaller (cài đặt bằng `pip install pyinstaller`)

## Cách đóng gói

### Đóng gói trên hệ điều hành hiện tại

Sử dụng script build tự động:

```bash
python build.py
```

Kết quả sẽ được lưu trong thư mục `dist/`.

### Đóng gói cho Windows

1. Trên Windows:
   ```bash
   python build.py
   ```

2. Từ macOS hoặc Linux (cần cài đặt Wine):
   ```bash
   # Cài đặt Wine trước (macOS)
   brew install wine-stable

   # Cài đặt PyInstaller cho Windows
   pip install pyinstaller
   
   # Chạy PyInstaller thông qua Wine
   wine pyinstaller --name=TifTiff --windowed --onefile --clean --add-data="resources;resources" --icon=icon.ico --version-file=version.txt app.py
   ```

### Đóng gói cho macOS

1. Trên macOS:
   ```bash
   python build.py
   ```

2. Từ các hệ điều hành khác:
   - Không thể đóng gói trực tiếp. Cần sử dụng máy ảo macOS hoặc máy thật.

### Đóng gói cho Linux

1. Trên Linux:
   ```bash
   python build.py
   ```

2. Từ các hệ điều hành khác:
   - Có thể sử dụng Docker để đóng gói:
   ```bash
   # Tạo Dockerfile
   echo "FROM python:3.8
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   RUN pip install pyinstaller
   RUN python build.py" > Dockerfile
   
   # Build Docker image
   docker build -t tiftiff-linux-build .
   
   # Copy kết quả từ container
   docker run --name tiftiff-build tiftiff-linux-build
   docker cp tiftiff-build:/app/dist ./dist-linux
   docker rm tiftiff-build
   ```

## Tạo bản cài đặt

### Windows

1. Tải và cài đặt [Inno Setup](https://jrsoftware.org/isdl.php)
2. Mở Inno Setup và tạo một script mới
3. Làm theo hướng dẫn để tạo installer từ file `dist/TifTiff.exe`

### macOS

Sử dụng `create-dmg` để tạo file DMG:

```bash
# Cài đặt create-dmg
brew install create-dmg

# Tạo DMG
create-dmg \
  --volname "TifTiff Installer" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "TifTiff.app" 200 190 \
  --hide-extension "TifTiff.app" \
  --app-drop-link 600 185 \
  "TifTiff.dmg" \
  "dist/TifTiff.app"
```

### Linux

Tạo gói `.deb` (cho Ubuntu/Debian):

```bash
# Cài đặt fpm
sudo gem install fpm

# Tạo gói .deb
fpm -s dir -t deb -n tiftiff -v 1.0.0 \
  --prefix=/usr/local \
  dist/TifTiff=/usr/local/bin/ \
  resources/=/usr/local/share/tiftiff/resources/
```

Hoặc tạo gói `.rpm` (cho Fedora/CentOS):

```bash
fpm -s dir -t rpm -n tiftiff -v 1.0.0 \
  --prefix=/usr/local \
  dist/TifTiff=/usr/local/bin/ \
  resources/=/usr/local/share/tiftiff/resources/
```

## Giải quyết vấn đề

Nếu gặp lỗi khi đóng gói:

1. Đảm bảo đã cài đặt tất cả các thư viện phụ thuộc
2. Kiểm tra đường dẫn đến các tài nguyên
3. Đối với macOS, nếu gặp lỗi quyền truy cập, chạy `sudo xattr -cr dist/TifTiff.app`
4. Đối với Linux, có thể cần thêm quyền thực thi: `chmod +x dist/TifTiff`

Để biết thêm thông tin, tham khảo [tài liệu PyInstaller](https://pyinstaller.org/en/stable/). 