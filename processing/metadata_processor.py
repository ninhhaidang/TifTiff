"""
Xử lý metadata của ảnh
"""

import os
import json
import csv
import time
from PIL import Image
import rasterio
import concurrent.futures
from collections import defaultdict
from datetime import datetime

class MetadataProcessor:
    """Lớp xử lý metadata của ảnh"""
    
    def __init__(self, logger=None):
        """Khởi tạo với tham số tùy chọn"""
        self.logger = logger
    
    def log(self, message):
        """Ghi log nếu logger được cung cấp"""
        if self.logger:
            self.logger(message)
    
    def extract_metadata_batch(self, file_paths, use_threads=True):
        """
        Trích xuất metadata từ nhiều ảnh cùng lúc
        
        Tham số:
            file_paths (list): Danh sách các đường dẫn đến ảnh
            use_threads (bool): Sử dụng đa luồng hay không
            
        Trả về:
            dict: Dictionary chứa metadata của từng ảnh
        """
        if not file_paths:
            return {}
            
        if use_threads and len(file_paths) > 1:
            # Sử dụng ThreadPoolExecutor để xử lý đa luồng
            results = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                # Submit các nhiệm vụ
                future_to_file = {
                    executor.submit(self.extract_metadata, file_path): file_path 
                    for file_path in file_paths
                }
                
                # Thu thập kết quả
                for future in concurrent.futures.as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        metadata = future.result()
                        if metadata:
                            results[file_path] = metadata
                    except Exception as e:
                        self.log(f"Lỗi khi xử lý metadata: {str(e)}")
            
            return results
        else:
            # Xử lý tuần tự
            return {
                file_path: self.extract_metadata(file_path)
                for file_path in file_paths
                if os.path.exists(file_path)
            }
    
    def extract_metadata(self, file_path):
        """
        Trích xuất metadata từ một ảnh
        
        Tham số:
            file_path (str): Đường dẫn đến ảnh
            
        Trả về:
            dict: Dictionary chứa metadata của ảnh
        """
        if not os.path.exists(file_path):
            return None
            
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Metadata cơ bản
        metadata = {
            "filename": filename,
            "path": file_path,
            "size": os.path.getsize(file_path),
            "size_human": self._format_file_size(os.path.getsize(file_path)),
            "format": file_ext[1:] if file_ext else "unknown",
            "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Thêm thông tin ảnh từ PIL
        try:
            with Image.open(file_path) as img:
                metadata.update({
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "channels": len(img.getbands()),
                    "bands": img.getbands(),
                    "dpi": img.info.get("dpi", "N/A")
                })
                
                # Thêm exif metadata nếu có
                if hasattr(img, "_getexif") and img._getexif():
                    exif = {
                        self._get_exif_tag_name(tag): value
                        for tag, value in img._getexif().items()
                        if self._get_exif_tag_name(tag) != str(tag)  # Chỉ lấy các tag có tên
                    }
                    metadata["exif"] = exif
        except Exception as e:
            self.log(f"Lỗi khi đọc metadata ảnh {filename}: {str(e)}")
        
        # Thêm thông tin địa lý nếu là ảnh GeoTIFF
        if file_ext.lower() in ['.tif', '.tiff']:
            try:
                with rasterio.open(file_path) as src:
                    if src.crs:
                        metadata.update({
                            "crs": str(src.crs),
                            "bounds": src.bounds,
                            "transform": [float(x) for x in src.transform],
                            "res": src.res
                        })
                        
                        # Đọc metadata từ GDAL tags
                        if src.tags():
                            metadata["gdal_metadata"] = src.tags()
            except Exception as e:
                self.log(f"Lỗi khi đọc metadata địa lý của {filename}: {str(e)}")
        
        return metadata
    
    def export_metadata_csv(self, file_paths, output_path):
        """
        Xuất metadata thành file CSV
        
        Tham số:
            file_paths (list): Danh sách các đường dẫn đến ảnh
            output_path (str): Đường dẫn đến file CSV đầu ra
            
        Trả về:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Lấy metadata từ tất cả các file
            metadata_dict = self.extract_metadata_batch(file_paths)
            
            if not metadata_dict:
                self.log("Không có dữ liệu metadata để xuất")
                return False
                
            # Tạo thư mục cho file đầu ra nếu chưa tồn tại
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Xác định tất cả các trường từ tất cả các file
            all_fields = set()
            for metadata in metadata_dict.values():
                all_fields.update(metadata.keys())
                
                # Thêm các trường con từ exif nếu có
                if "exif" in metadata and isinstance(metadata["exif"], dict):
                    all_fields.update(f"exif.{key}" for key in metadata["exif"].keys())
                
                # Thêm các trường con từ gdal_metadata nếu có
                if "gdal_metadata" in metadata and isinstance(metadata["gdal_metadata"], dict):
                    all_fields.update(f"gdal.{key}" for key in metadata["gdal_metadata"].keys())
            
            # Sắp xếp các trường
            sorted_fields = sorted(list(all_fields))
            
            # Xuất ra file CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Viết header
                writer.writerow(['filename'] + [f for f in sorted_fields if f != 'filename'])
                
                # Viết dữ liệu
                for file_path, metadata in metadata_dict.items():
                    row = [os.path.basename(file_path)]
                    
                    for field in sorted_fields:
                        if field == 'filename':
                            continue
                            
                        # Xử lý các trường con
                        if field.startswith('exif.'):
                            _, exif_field = field.split('.', 1)
                            value = metadata.get('exif', {}).get(exif_field, '')
                        elif field.startswith('gdal.'):
                            _, gdal_field = field.split('.', 1)
                            value = metadata.get('gdal_metadata', {}).get(gdal_field, '')
                        else:
                            value = metadata.get(field, '')
                            
                        # Đảm bảo giá trị có thể ghi vào CSV
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, ensure_ascii=False)
                            
                        row.append(value)
                        
                    writer.writerow(row)
            
            self.log(f"Đã xuất metadata ra file CSV: {output_path}")
            return output_path
            
        except Exception as e:
            self.log(f"Lỗi khi xuất metadata CSV: {str(e)}")
            return False
    
    def export_metadata_json(self, file_paths, output_path):
        """
        Xuất metadata thành file JSON
        
        Tham số:
            file_paths (list): Danh sách các đường dẫn đến ảnh
            output_path (str): Đường dẫn đến file JSON đầu ra
            
        Trả về:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Lấy metadata từ tất cả các file
            metadata_dict = self.extract_metadata_batch(file_paths)
            
            if not metadata_dict:
                self.log("Không có dữ liệu metadata để xuất")
                return False
            
            # Tạo thư mục cho file đầu ra nếu chưa tồn tại
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Chuẩn bị dữ liệu để xuất
            # Sử dụng tên file làm key thay vì đường dẫn đầy đủ
            export_data = {
                os.path.basename(file_path): metadata
                for file_path, metadata in metadata_dict.items()
            }
            
            # Thêm metadata tổng hợp
            summary = {
                "total_files": len(metadata_dict),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "formats": self._count_formats(metadata_dict.values()),
                "total_size": sum(m.get("size", 0) for m in metadata_dict.values()),
                "total_size_human": self._format_file_size(sum(m.get("size", 0) for m in metadata_dict.values()))
            }
            
            export_data["__summary__"] = summary
            
            # Xuất ra file JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            self.log(f"Đã xuất metadata ra file JSON: {output_path}")
            return output_path
            
        except Exception as e:
            self.log(f"Lỗi khi xuất metadata JSON: {str(e)}")
            return False
    
    def _format_file_size(self, size_bytes):
        """Chuyển đổi kích thước từ byte sang đơn vị thích hợp"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"
    
    def _count_formats(self, metadata_list):
        """Đếm số lượng các định dạng ảnh"""
        formats = defaultdict(int)
        for metadata in metadata_list:
            fmt = metadata.get("format", "unknown")
            formats[fmt] += 1
        return dict(formats)
    
    def _get_exif_tag_name(self, tag):
        """Chuyển đổi mã EXIF thành tên có ý nghĩa"""
        # EXIF tags phổ biến
        EXIF_TAGS = {
            256: "ImageWidth",
            257: "ImageHeight",
            258: "BitsPerSample",
            259: "Compression",
            270: "ImageDescription",
            271: "Make",
            272: "Model",
            274: "Orientation",
            282: "XResolution",
            283: "YResolution",
            296: "ResolutionUnit",
            305: "Software",
            306: "DateTime",
            315: "Artist",
            316: "HostComputer",
            331: "DocumentName",
            36864: "ExifVersion",
            36867: "DateTimeOriginal",
            36868: "DateTimeDigitized",
            37121: "ComponentsConfiguration",
            37122: "CompressedBitsPerPixel",
            37377: "ShutterSpeedValue",
            37378: "ApertureValue",
            37379: "BrightnessValue",
            37380: "ExposureBiasValue",
            37381: "MaxApertureValue",
            37382: "SubjectDistance",
            37383: "MeteringMode",
            37384: "LightSource",
            37385: "Flash",
            37386: "FocalLength",
            37520: "SubsecTime",
            37521: "SubsecTimeOriginal",
            37522: "SubsecTimeDigitized",
            40960: "FlashpixVersion",
            40961: "ColorSpace",
            40962: "PixelXDimension",
            40963: "PixelYDimension",
            40964: "RelatedSoundFile",
            41728: "FileSource",
            41729: "SceneType",
            41985: "CustomRendered",
            41986: "ExposureMode",
            41987: "WhiteBalance",
            41988: "DigitalZoomRatio",
            41989: "FocalLengthIn35mmFilm",
            41990: "SceneCaptureType",
            41991: "GainControl",
            41992: "Contrast",
            41993: "Saturation",
            41994: "Sharpness",
            42032: "CameraOwnerName",
            42033: "BodySerialNumber",
            42034: "LensSpecification",
            42035: "LensMake",
            42036: "LensModel",
            42037: "LensSerialNumber",
            42240: "Gamma"
        }
        
        return EXIF_TAGS.get(tag, str(tag)) 