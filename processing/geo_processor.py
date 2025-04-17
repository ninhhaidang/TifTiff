"""
Xử lý dữ liệu địa lý cho ảnh GeoTIFF
"""

import os
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.errors import RasterioIOError, CRSError
import concurrent.futures
from resources.constants import COMMON_CRS

class GeoProcessor:
    """Lớp xử lý dữ liệu địa lý cho ảnh GeoTIFF"""
    
    def __init__(self, logger=None):
        """Khởi tạo với tham số tùy chọn"""
        self.logger = logger
        self.common_crs = COMMON_CRS
    
    def log(self, message):
        """Ghi log nếu logger được cung cấp"""
        if self.logger:
            self.logger.log(message)
    
    def detect_crs(self, file_path):
        """Phát hiện hệ tọa độ từ file GeoTIFF"""
        try:
            with rasterio.open(file_path) as src:
                if src.crs:
                    return str(src.crs)
                else:
                    return None
        except Exception as e:
            self.log(f"❌ {self._('error_prefix')}: {self._('crs_read_error')} - {str(e)}")
            return None
    
    def batch_reproject(self, input_files, output_dir, dst_crs, options=None):
        """Chuyển đổi hệ tọa độ hàng loạt sử dụng đa luồng"""
        if not input_files:
            return []
        
        # Sử dụng ThreadPoolExecutor để xử lý đa luồng
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # Submit các nhiệm vụ
            future_to_file = {
                executor.submit(self.reproject_raster, src_path, 
                                os.path.join(output_dir, os.path.basename(src_path)),
                                dst_crs, options): src_path 
                for src_path in input_files
            }
            
            # Thu thập kết quả
            results = []
            for future in concurrent.futures.as_completed(future_to_file):
                src_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    self.log(f"❌ {self._('error_prefix')}: {self._('processing_error')} {os.path.basename(src_path)} - {str(e)}")
            
            return results
    
    def reproject_raster(self, src_path, dst_path, dst_crs, options=None):
        """
        Chuyển đổi hệ tọa độ của một ảnh GeoTIFF
        
        Tham số:
            src_path (str): Đường dẫn đến ảnh nguồn
            dst_path (str): Đường dẫn đến ảnh đích
            dst_crs (str): Hệ tọa độ đích (e.g., 'EPSG:4326')
            options (dict): Các tùy chọn bổ sung
        
        Trả về:
            str: Đường dẫn đến ảnh đã chuyển đổi hoặc None nếu có lỗi
        """
        try:
            # Đảm bảo thư mục đích tồn tại
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            with rasterio.open(src_path) as src:
                # Kiểm tra xem file có hệ tọa độ không
                if not src.crs:
                    self.log(f"⚠️ {self._('warning_prefix')}: {os.path.basename(src_path)} {self._('missing_crs')}")
                    return None
                
                # Tính toán transformation
                transform, width, height = calculate_default_transform(
                    src.crs, dst_crs, src.width, src.height, *src.bounds)
                
                # Cập nhật metadata cho ảnh đầu ra
                out_kwargs = src.meta.copy()
                out_kwargs.update({
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height,
                    'driver': self._get_driver_from_path(dst_path)
                })
                
                # Thêm các tùy chọn bổ sung nếu có
                if options and isinstance(options, dict):
                    out_kwargs.update(options)
                
                # Tạo file đầu ra và thực hiện reproject
                with rasterio.open(dst_path, 'w', **out_kwargs) as dst:
                    # Reproject từng band
                    for i in range(1, src.count + 1):
                        # Đọc dữ liệu từ band gốc
                        source = src.read(i)
                        
                        # Chuẩn bị một mảng rỗng cho dữ liệu đầu ra
                        destination = np.zeros((height, width), dtype=source.dtype)
                        
                        # Thực hiện reproject
                        reproject(
                            source,
                            destination,
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=transform,
                            dst_crs=dst_crs,
                            resampling=Resampling.nearest
                        )
                        
                        # Ghi dữ liệu vào band trong file đầu ra
                        dst.write(destination, i)
                
                self.log(f"✅ {self._('success_prefix')}: {self._('reprojected')} {src.crs} → {dst_crs} {self._('for')} {os.path.basename(dst_path)}")
                return dst_path
                
        except (RasterioIOError, CRSError) as e:
            self.log(f"❌ {self._('error_prefix')}: {self._('reprojection_error')} {os.path.basename(src_path)} - {str(e)}")
            return None
        except Exception as e:
            self.log(f"❌ {self._('error_prefix')}: {self._('unknown_error')} - {str(e)}")
            return None
    
    def _get_driver_from_path(self, file_path):
        """Xác định GDAL driver dựa trên phần mở rộng của file"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Map các định dạng phổ biến tới driver tương ứng
        drivers = {
            '.tif': 'GTiff',
            '.tiff': 'GTiff',
            '.png': 'PNG',
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.vrt': 'VRT',
            '.jp2': 'JP2OpenJPEG',
            '.img': 'HFA',
            '.nc': 'netCDF',
            '.grd': 'AIG',
            '.mbtiles': 'MBTiles',
            '.gpkg': 'GPKG',
            '.shp': 'ESRI Shapefile'
        }
        
        return drivers.get(ext, 'GTiff')  # Mặc định là GTiff
            
    def save_with_geospatial(self, image, output_path, geo_metadata):
        """Lưu ảnh PIL với thông tin địa lý"""
        try:
            # Chuyển đổi từ PIL Image sang numpy array để sử dụng với rasterio
            array = np.array(image)
            
            # Xác định driver dựa trên phần mở rộng file
            ext = os.path.splitext(output_path)[1]
            driver = self._get_driver_from_path(output_path)
            
            # Tạo file raster mới với thông tin địa lý
            with rasterio.open(
                output_path, 'w', 
                driver=driver,
                width=geo_metadata['width'], 
                height=geo_metadata['height'],
                count=array.shape[2], 
                dtype=array.dtype,
                crs=geo_metadata['crs'], 
                transform=geo_metadata['transform']
            ) as dst:
                # Ghi từng kênh màu (RGBA hoặc RGB)
                for i in range(array.shape[2]):
                    dst.write(array[:, :, i], i+1)
            
            if self.logger:
                self.logger.log(f"✅ {self._('success_prefix')}: {self._('saved_with_crs')} {geo_metadata['crs']}")
                
            return True
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('geospatial_save_error')} - {e}")
            return False
            
    def extract_geo_metadata(self, image_path, dst_crs, source_crs=None):
        """Trích xuất metadata địa lý từ ảnh GeoTIFF"""
        try:
            with rasterio.open(image_path) as src:
                src_crs = source_crs or src.crs
                
                if not src_crs:
                    if self.logger:
                        self.logger.log(f"⚠️ {self._('warning_prefix')}: {self._('no_source_crs')}")
                    return None
                    
                # Tính toán transform cho hệ tọa độ đích
                transform, width, height = calculate_default_transform(
                    src_crs, dst_crs, src.width, src.height, *src.bounds
                )
                
                # Tạo metadata
                geo_metadata = {
                    'crs': dst_crs,
                    'transform': transform,
                    'width': width,
                    'height': height,
                    'count': src.count,
                    'dtype': src.dtypes[0]
                }
                
                return geo_metadata
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('metadata_extraction_error')} - {e}")
            return None
            
    def update_geo_metadata_scale(self, geo_metadata, scale):
        """Cập nhật metadata địa lý khi thay đổi kích thước ảnh"""
        if not geo_metadata or scale == 1.0:
            return geo_metadata
            
        try:
            # Tạo bản sao metadata
            updated_metadata = geo_metadata.copy()
            
            # Cập nhật kích thước
            updated_metadata['width'] = int(geo_metadata['width'] * scale)
            updated_metadata['height'] = int(geo_metadata['height'] * scale)
            
            # Cập nhật transform (tỷ lệ pixel)
            transform = geo_metadata['transform']
            updated_metadata['transform'] = rasterio.Affine(
                transform.a / scale, transform.b, transform.c,
                transform.d, transform.e / scale, transform.f
            )
            
            return updated_metadata
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('metadata_update_error')} - {e}")
            return geo_metadata 