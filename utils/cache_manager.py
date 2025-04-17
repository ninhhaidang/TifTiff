import os
import json
import time
import hashlib
import shutil
from functools import lru_cache
from datetime import datetime, timedelta
import threading

class CacheManager:
    """Quản lý cache để tăng hiệu suất ứng dụng"""
    
    def __init__(self, cache_dir=None, max_size_mb=500, max_age_days=7, logger=None):
        """
        Khởi tạo cache manager
        
        Tham số:
            cache_dir (str): Thư mục lưu cache
            max_size_mb (int): Kích thước tối đa của cache (MB)
            max_age_days (int): Thời gian tối đa để giữ cache (ngày)
            logger (callable): Hàm logger
        """
        # Thiết lập thư mục cache
        if cache_dir is None:
            app_data = os.getenv('APPDATA') or os.path.expanduser('~/.config')
            cache_dir = os.path.join(app_data, 'TifTiff', 'cache')
        
        self.cache_dir = cache_dir
        self.max_size = max_size_mb * 1024 * 1024  # Chuyển đổi sang bytes
        self.max_age = timedelta(days=max_age_days)
        self.logger = logger
        self.lock = threading.RLock()
        
        # Tạo thư mục cache nếu chưa tồn tại
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Khởi tạo metadata cache
        self.metadata_file = os.path.join(self.cache_dir, 'metadata.json')
        self.metadata = self._load_metadata()
        
        # Chạy dọn dẹp cache nếu cần
        self._cleanup_if_needed()
    
    def log(self, message):
        """Ghi log nếu logger được cung cấp"""
        if self.logger:
            self.logger(message)
    
    def _load_metadata(self):
        """Tải metadata của cache từ file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Lỗi khi đọc metadata cache: {str(e)}")
        
        # Trả về metadata trống nếu không đọc được
        return {
            'last_cleanup': datetime.now().isoformat(),
            'entries': {}
        }
    
    def _save_metadata(self):
        """Lưu metadata của cache ra file"""
        try:
            with self.lock:
                with open(self.metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"Lỗi khi lưu metadata cache: {str(e)}")
    
    def _get_cache_key(self, data):
        """Tạo khóa cache từ dữ liệu"""
        if isinstance(data, str):
            # Nếu là đường dẫn file, sử dụng nội dung file để tạo hash
            if os.path.exists(data):
                try:
                    with open(data, 'rb') as f:
                        file_hash = hashlib.md5()
                        for chunk in iter(lambda: f.read(4096), b''):
                            file_hash.update(chunk)
                        return file_hash.hexdigest()
                except Exception:
                    # Nếu không đọc được file, sử dụng đường dẫn
                    return hashlib.md5(data.encode('utf-8')).hexdigest()
            else:
                # Chuỗi thông thường
                return hashlib.md5(data.encode('utf-8')).hexdigest()
        elif isinstance(data, (list, tuple)):
            # Kết hợp hash của từng phần tử
            combined = ''.join(self._get_cache_key(item) for item in data)
            return hashlib.md5(combined.encode('utf-8')).hexdigest()
        elif isinstance(data, dict):
            # Sắp xếp theo key và tạo hash
            sorted_items = sorted(data.items())
            return self._get_cache_key(str(sorted_items))
        else:
            # Các kiểu dữ liệu khác
            return hashlib.md5(str(data).encode('utf-8')).hexdigest()
    
    def _cleanup_if_needed(self):
        """Kiểm tra và dọn dẹp cache nếu cần"""
        last_cleanup_str = self.metadata.get('last_cleanup', '')
        try:
            last_cleanup = datetime.fromisoformat(last_cleanup_str)
            # Dọn dẹp mỗi ngày
            if datetime.now() - last_cleanup > timedelta(days=1):
                threading.Thread(target=self._cleanup_cache, daemon=True).start()
        except Exception:
            # Nếu không đọc được ngày, dọn dẹp luôn
            threading.Thread(target=self._cleanup_cache, daemon=True).start()
    
    def _cleanup_cache(self):
        """Dọn dẹp các mục cache cũ hoặc khi vượt quá kích thước"""
        with self.lock:
            try:
                now = datetime.now()
                self.metadata['last_cleanup'] = now.isoformat()
                
                # Xóa các mục quá cũ
                entries_to_remove = []
                for cache_key, entry in self.metadata['entries'].items():
                    try:
                        created_at = datetime.fromisoformat(entry['created_at'])
                        if now - created_at > self.max_age:
                            entries_to_remove.append(cache_key)
                    except Exception:
                        entries_to_remove.append(cache_key)
                
                # Xóa các file và metadata
                for cache_key in entries_to_remove:
                    self._remove_cache_entry(cache_key)
                
                # Kiểm tra kích thước cache
                cache_size = self._get_cache_size()
                if cache_size > self.max_size:
                    self._reduce_cache_size(cache_size)
                
                # Lưu metadata
                self._save_metadata()
                
            except Exception as e:
                self.log(f"Lỗi khi dọn dẹp cache: {str(e)}")
    
    def _get_cache_size(self):
        """Tính tổng kích thước của cache"""
        total_size = 0
        for dirpath, _, filenames in os.walk(self.cache_dir):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size
    
    def _reduce_cache_size(self, current_size):
        """Giảm kích thước cache bằng cách xóa các mục ít sử dụng nhất"""
        with self.lock:
            # Sắp xếp theo thời gian truy cập
            entries = [(k, v) for k, v in self.metadata['entries'].items()]
            entries.sort(key=lambda x: x[1].get('last_accessed', ''))
            
            # Xóa các mục cho đến khi đạt kích thước mong muốn
            target_size = self.max_size * 0.8  # Giảm xuống 80% kích thước tối đa
            for cache_key, _ in entries:
                self._remove_cache_entry(cache_key)
                current_size = self._get_cache_size()
                if current_size < target_size:
                    break
    
    def _remove_cache_entry(self, cache_key):
        """Xóa một mục cache"""
        try:
            # Xóa file cache
            cache_path = os.path.join(self.cache_dir, cache_key)
            if os.path.exists(cache_path):
                if os.path.isfile(cache_path):
                    os.remove(cache_path)
                elif os.path.isdir(cache_path):
                    shutil.rmtree(cache_path)
            
            # Xóa metadata
            if cache_key in self.metadata['entries']:
                del self.metadata['entries'][cache_key]
        except Exception as e:
            self.log(f"Lỗi khi xóa mục cache {cache_key}: {str(e)}")
    
    def has_cache(self, data, category=None):
        """
        Kiểm tra xem dữ liệu có trong cache không
        
        Tham số:
            data: Dữ liệu cần kiểm tra (chuỗi, danh sách, từ điển, ...)
            category (str): Danh mục cache (tùy chọn)
            
        Trả về:
            bool: True nếu có trong cache, False nếu không
        """
        cache_key = self._get_cache_key(data)
        if category:
            cache_key = f"{category}_{cache_key}"
        
        with self.lock:
            # Kiểm tra trong metadata
            if cache_key in self.metadata['entries']:
                # Kiểm tra file cache có tồn tại không
                cache_path = os.path.join(self.cache_dir, cache_key)
                if os.path.exists(cache_path):
                    # Cập nhật thời gian truy cập
                    self.metadata['entries'][cache_key]['last_accessed'] = datetime.now().isoformat()
                    self._save_metadata()
                    return True
                else:
                    # Nếu file không tồn tại, xóa metadata
                    del self.metadata['entries'][cache_key]
                    self._save_metadata()
        
        return False
    
    def get_cache(self, data, category=None):
        """
        Lấy dữ liệu từ cache
        
        Tham số:
            data: Dữ liệu cần lấy cache (chuỗi, danh sách, từ điển, ...)
            category (str): Danh mục cache (tùy chọn)
            
        Trả về:
            object: Dữ liệu cache hoặc None nếu không có
        """
        cache_key = self._get_cache_key(data)
        if category:
            cache_key = f"{category}_{cache_key}"
        
        with self.lock:
            if not self.has_cache(data, category):
                return None
            
            cache_path = os.path.join(self.cache_dir, cache_key)
            try:
                # Đọc file cache
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"Lỗi khi đọc cache: {str(e)}")
                return None
    
    def set_cache(self, data, value, category=None):
        """
        Lưu dữ liệu vào cache
        
        Tham số:
            data: Dữ liệu cần cache (chuỗi, danh sách, từ điển, ...)
            value: Giá trị cần lưu (phải có thể serialize bằng json)
            category (str): Danh mục cache (tùy chọn)
            
        Trả về:
            bool: True nếu thành công, False nếu thất bại
        """
        cache_key = self._get_cache_key(data)
        if category:
            cache_key = f"{category}_{cache_key}"
        
        with self.lock:
            try:
                # Lưu dữ liệu vào file cache
                cache_path = os.path.join(self.cache_dir, cache_key)
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(value, f, ensure_ascii=False)
                
                # Cập nhật metadata
                now = datetime.now().isoformat()
                self.metadata['entries'][cache_key] = {
                    'created_at': now,
                    'last_accessed': now,
                    'category': category or 'default'
                }
                self._save_metadata()
                
                return True
            except Exception as e:
                self.log(f"Lỗi khi lưu cache: {str(e)}")
                return False
    
    def clear_cache(self, category=None):
        """
        Xóa toàn bộ cache hoặc chỉ một danh mục
        
        Tham số:
            category (str): Danh mục cần xóa (None để xóa tất cả)
            
        Trả về:
            int: Số lượng mục đã xóa
        """
        with self.lock:
            entries_to_remove = []
            
            if category:
                # Xóa theo danh mục
                for cache_key, entry in self.metadata['entries'].items():
                    if entry.get('category') == category:
                        entries_to_remove.append(cache_key)
            else:
                # Xóa tất cả
                entries_to_remove = list(self.metadata['entries'].keys())
            
            # Xóa từng mục
            for cache_key in entries_to_remove:
                self._remove_cache_entry(cache_key)
            
            # Lưu metadata
            self._save_metadata()
            
            return len(entries_to_remove)
    
    def get_cache_info(self):
        """
        Lấy thông tin về cache
        
        Trả về:
            dict: Thông tin về cache
        """
        with self.lock:
            categories = {}
            total_entries = len(self.metadata['entries'])
            
            # Đếm số lượng theo danh mục
            for entry in self.metadata['entries'].values():
                category = entry.get('category', 'default')
                categories[category] = categories.get(category, 0) + 1
            
            # Tính kích thước
            cache_size = self._get_cache_size()
            
            return {
                'total_entries': total_entries,
                'total_size': cache_size,
                'total_size_human': self._format_size(cache_size),
                'categories': categories,
                'last_cleanup': self.metadata.get('last_cleanup', '')
            }
    
    @staticmethod
    def _format_size(size_bytes):
        """Định dạng kích thước"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"

# Tạo instance toàn cục
cache_manager = CacheManager()

# Hàm wrapper tiện lợi
@lru_cache(maxsize=128)
def cached_function(func):
    """
    Decorator để cache kết quả của hàm
    
    Ví dụ:
        @cached_function
        def expensive_operation(param1, param2):
            # Xử lý tốn thời gian
            return result
    """
    def wrapper(*args, **kwargs):
        # Tạo key từ tên hàm và tham số
        cache_key = (func.__name__, args, frozenset(kwargs.items()))
        
        # Kiểm tra cache
        result = cache_manager.get_cache(cache_key, category='function')
        if result is not None:
            return result
        
        # Tính toán kết quả
        result = func(*args, **kwargs)
        
        # Lưu vào cache
        cache_manager.set_cache(cache_key, result, category='function')
        
        return result
        
    return wrapper 