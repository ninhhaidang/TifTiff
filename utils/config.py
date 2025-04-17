"""
Xử lý lưu và đọc cấu hình cho ứng dụng TifTiff
"""

import os
import json
import threading
from .cache_manager import cache_manager

class Config:
    """Quản lý cấu hình ứng dụng"""
    
    def __init__(self, config_file="config.json", default_config=None, logger=None):
        """
        Khởi tạo quản lý cấu hình
        
        Tham số:
            config_file (str): Đường dẫn đến file cấu hình
            default_config (dict): Cấu hình mặc định
            logger (callable): Hàm logger
        """
        self.config_file = config_file
        self.config = {}
        self.logger = logger
        self.lock = threading.RLock()
        self.default_config = default_config or {
            "language": "vi",
            "theme": "cosmo",
            "last_input_dir": "",
            "last_output_dir": "",
            "export_format": "PNG",
            "scale_ratio": 1.0,
            "enable_geo": False,
            "target_crs": "EPSG:4326",
            "remove_black": False,
            "remove_white": False,
            "save_geo": True,
            "geo_format": "GTiff",
            "brightness": 1.0,
            "contrast": 1.0,
            "saturation": 1.0
        }
        
        # Tải cấu hình
        self.load_config()
    
    def log(self, message):
        """Ghi log nếu logger được cung cấp"""
        if self.logger:
            self.logger(message)
    
    def load_config(self):
        """Tải cấu hình từ file"""
        with self.lock:
            try:
                if os.path.exists(self.config_file):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded_config = json.load(f)
                        
                    # Cập nhật cấu hình với giá trị đã tải
                    self.config = self.default_config.copy()
                    self.config.update(loaded_config)
                else:
                    # Sử dụng cấu hình mặc định
                    self.config = self.default_config.copy()
                    self.save_config()
            except Exception as e:
                self.log(f"Lỗi khi tải cấu hình: {str(e)}")
                # Sử dụng cấu hình mặc định nếu có lỗi
                self.config = self.default_config.copy()
    
    def save_config(self):
        """Lưu cấu hình ra file"""
        with self.lock:
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                return True
            except Exception as e:
                self.log(f"Lỗi khi lưu cấu hình: {str(e)}")
                return False
    
    def get(self, key, default=None):
        """
        Lấy giá trị cấu hình
        
        Tham số:
            key (str): Khóa cấu hình cần lấy
            default: Giá trị mặc định nếu không tìm thấy khóa
            
        Trả về:
            Giá trị cấu hình hoặc giá trị mặc định
        """
        with self.lock:
            return self.config.get(key, default)
    
    def set(self, key, value, save=True):
        """
        Đặt giá trị cấu hình
        
        Tham số:
            key (str): Khóa cấu hình cần đặt
            value: Giá trị cần đặt
            save (bool): Có lưu cấu hình ra file không
            
        Trả về:
            bool: True nếu thành công, False nếu thất bại
        """
        with self.lock:
            self.config[key] = value
            
            # Cache giá trị mới
            cache_manager.set_cache(f"config_{key}", value, category="config")
            
            if save:
                return self.save_config()
            return True
    
    def get_all(self):
        """
        Lấy tất cả cấu hình
        
        Trả về:
            dict: Toàn bộ cấu hình
        """
        with self.lock:
            return self.config.copy()
    
    def update(self, new_config, save=True):
        """
        Cập nhật nhiều cấu hình cùng lúc
        
        Tham số:
            new_config (dict): Cấu hình mới
            save (bool): Có lưu cấu hình ra file không
            
        Trả về:
            bool: True nếu thành công, False nếu thất bại
        """
        with self.lock:
            self.config.update(new_config)
            
            # Cache các giá trị mới
            for key, value in new_config.items():
                cache_manager.set_cache(f"config_{key}", value, category="config")
            
            if save:
                return self.save_config()
            return True
    
    def reset(self, save=True):
        """
        Đặt lại cấu hình về mặc định
        
        Tham số:
            save (bool): Có lưu cấu hình ra file không
            
        Trả về:
            bool: True nếu thành công, False nếu thất bại
        """
        with self.lock:
            self.config = self.default_config.copy()
            
            # Xóa cache
            cache_manager.clear_cache(category="config")
            
            if save:
                return self.save_config()
            return True

# Tạo instance toàn cục
config_manager = Config()

# Hàm wrapper tiện lợi
def get_config(key, default=None):
    """Lấy giá trị cấu hình từ instance toàn cục"""
    # Thử lấy từ cache trước
    cached_value = cache_manager.get_cache(f"config_{key}", category="config")
    if cached_value is not None:
        return cached_value
    
    # Nếu không có trong cache, lấy từ config
    value = config_manager.get(key, default)
    
    # Lưu vào cache
    cache_manager.set_cache(f"config_{key}", value, category="config")
    
    return value

def set_config(key, value, save=True):
    """Đặt giá trị cấu hình vào instance toàn cục"""
    return config_manager.set(key, value, save) 