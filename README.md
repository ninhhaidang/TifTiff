# TifTiff - Image Processing Tool | Phần mềm xử lý ảnh

## English | Tiếng Anh

TifTiff is a powerful, user-friendly tool for processing and converting image files, with special capabilities for handling geospatial data in GeoTIFF format.

![TifTiff Application](screenshots/app.png)

### Features

- **Basic Image Processing**:
  - Convert between different image formats (PNG, JPEG, TIFF, etc.)
  - Resize images with custom scaling
  - Remove black or white backgrounds
  - Adjust brightness, contrast, and saturation

- **Geospatial Processing**:
  - Convert between different coordinate systems (EPSG:4326, EPSG:3857, etc.)
  - Preserve geospatial metadata when converting formats
  - Support for multiple geospatial output formats (GeoTIFF, GeoJPEG2000, ERDAS Imagine)
  - Automatic coordinate system detection

- **Metadata Handling**:
  - Extract and view image metadata
  - Export metadata to CSV or JSON formats
  - Comprehensive metadata support for EXIF and geospatial information

- **User Interface**:
  - Intuitive tab-based interface
  - Dark and light themes
  - Multiple language support (English, Vietnamese)
  - Progress tracking and detailed logs
  - Drag and drop support

### Installation

#### Requirements
- Python 3.8 or higher
- Required Python packages:
  - PIL/Pillow
  - Rasterio
  - NumPy
  - ttkbootstrap
  - tkinterdnd2

#### Method 1: Run from Source
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/TifTiff.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app.py
   ```

#### Method 2: Download Executable
1. Download the latest release from the [Releases](https://github.com/yourusername/TifTiff/releases) page
2. Extract the zip file to your desired location
3. Run `TifTiff.exe`

### Usage

#### Basic Image Processing
1. Select the source image(s) or folder using the "Select Files" or "Select Folder" buttons
2. Choose an output folder where processed images will be saved
3. Set your desired output format and scaling options
4. Use the "Advanced" tab to adjust brightness, contrast, and saturation if needed
5. Click "Start Processing" to begin the conversion

#### Geospatial Processing
1. Select GeoTIFF source images
2. Go to the "Coordinates" tab and enable coordinate system transformation
3. Select your target coordinate system
4. Choose whether to preserve geospatial information in the output
5. Select your preferred geospatial output format
6. Click "Start Processing" to begin the conversion

#### Exporting Metadata
1. Select the source image(s) or folder
2. Go to the "Options" tab
3. Click "Export CSV" or "Export JSON" to extract and save the metadata

### Configuration
TifTiff automatically saves your settings between sessions, including:
- Theme preferences
- Language selection
- Last used input/output directories
- Processing options

### Language Support
To change the application language:
1. Go to the "Options" tab
2. Select your preferred language from the dropdown menu

### License
This software is released under the [MIT License](LICENSE).

### Credits
TifTiff is developed by [Your Name/Organization]. It leverages the following open-source libraries:
- [Pillow](https://python-pillow.org/) for image processing
- [Rasterio](https://rasterio.readthedocs.io/) for geospatial operations
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) for the modern UI
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) for drag and drop support

---

## Tiếng Việt | Vietnamese

TifTiff là công cụ mạnh mẽ, thân thiện với người dùng để xử lý và chuyển đổi các tệp hình ảnh, với khả năng đặc biệt xử lý dữ liệu không gian địa lý ở định dạng GeoTIFF.

![Ứng dụng TifTiff](screenshots/app.png)

### Tính năng

- **Xử lý ảnh cơ bản**:
  - Chuyển đổi giữa các định dạng hình ảnh khác nhau (PNG, JPEG, TIFF, v.v.)
  - Thay đổi kích thước hình ảnh với tỷ lệ tùy chỉnh
  - Xóa nền đen hoặc trắng
  - Điều chỉnh độ sáng, độ tương phản và độ bão hòa

- **Xử lý dữ liệu không gian địa lý**:
  - Chuyển đổi giữa các hệ tọa độ khác nhau (EPSG:4326, EPSG:3857, v.v.)
  - Bảo toàn metadata không gian địa lý khi chuyển đổi định dạng
  - Hỗ trợ nhiều định dạng đầu ra không gian địa lý (GeoTIFF, GeoJPEG2000, ERDAS Imagine)
  - Tự động phát hiện hệ tọa độ

- **Quản lý metadata**:
  - Trích xuất và xem metadata hình ảnh
  - Xuất metadata sang định dạng CSV hoặc JSON
  - Hỗ trợ toàn diện cho thông tin EXIF và thông tin không gian địa lý

- **Giao diện người dùng**:
  - Giao diện dựa trên tab trực quan
  - Chủ đề sáng và tối
  - Hỗ trợ nhiều ngôn ngữ (Tiếng Anh, Tiếng Việt)
  - Theo dõi tiến trình và nhật ký chi tiết
  - Hỗ trợ kéo và thả

### Cài đặt

#### Yêu cầu
- Python 3.8 trở lên
- Các gói Python cần thiết:
  - PIL/Pillow
  - Rasterio
  - NumPy
  - ttkbootstrap
  - tkinterdnd2

#### Phương pháp 1: Chạy từ mã nguồn
1. Sao chép kho lưu trữ này:
   ```
   git clone https://github.com/yourusername/TifTiff.git
   ```

2. Cài đặt các gói phụ thuộc cần thiết:
   ```
   pip install -r requirements.txt
   ```

3. Chạy ứng dụng:
   ```
   python app.py
   ```

#### Phương pháp 2: Tải xuống tệp thực thi
1. Tải xuống phiên bản mới nhất từ trang [Releases](https://github.com/yourusername/TifTiff/releases)
2. Giải nén tệp zip đến vị trí mong muốn của bạn
3. Chạy `TifTiff.exe`

### Cách sử dụng

#### Xử lý ảnh cơ bản
1. Chọn (các) hình ảnh nguồn hoặc thư mục bằng nút "Chọn file" hoặc "Chọn thư mục"
2. Chọn thư mục đầu ra nơi hình ảnh đã xử lý sẽ được lưu
3. Đặt định dạng đầu ra và tùy chọn tỷ lệ mong muốn
4. Sử dụng tab "Nâng cao" để điều chỉnh độ sáng, độ tương phản và độ bão hòa nếu cần
5. Nhấp vào "Bắt đầu xử lý" để bắt đầu chuyển đổi

#### Xử lý không gian địa lý
1. Chọn hình ảnh nguồn GeoTIFF
2. Chuyển đến tab "Hệ tọa độ" và bật chuyển đổi hệ tọa độ
3. Chọn hệ tọa độ đích của bạn
4. Chọn có lưu thông tin không gian địa lý trong đầu ra hay không
5. Chọn định dạng đầu ra không gian địa lý ưa thích của bạn
6. Nhấp vào "Bắt đầu xử lý" để bắt đầu chuyển đổi

#### Xuất metadata
1. Chọn (các) hình ảnh nguồn hoặc thư mục
2. Chuyển đến tab "Tùy chọn"
3. Nhấp vào "Xuất CSV" hoặc "Xuất JSON" để trích xuất và lưu metadata

### Cấu hình
TifTiff tự động lưu cài đặt của bạn giữa các phiên, bao gồm:
- Tùy chọn chủ đề
- Lựa chọn ngôn ngữ
- Thư mục nhập/xuất được sử dụng lần cuối
- Tùy chọn xử lý

### Hỗ trợ ngôn ngữ
Để thay đổi ngôn ngữ ứng dụng:
1. Chuyển đến tab "Tùy chọn"
2. Chọn ngôn ngữ ưa thích của bạn từ menu thả xuống

### Giấy phép
Phần mềm này được phát hành theo [Giấy phép MIT](LICENSE).

### Công nhận
TifTiff được phát triển bởi [Tên/Tổ chức của bạn]. Nó tận dụng các thư viện mã nguồn mở sau:
- [Pillow](https://python-pillow.org/) cho xử lý hình ảnh
- [Rasterio](https://rasterio.readthedocs.io/) cho hoạt động không gian địa lý
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) cho giao diện người dùng hiện đại
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) cho hỗ trợ kéo và thả
