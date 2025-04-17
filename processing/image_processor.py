"""
Xử lý hình ảnh cơ bản
"""

import os
import time
import numpy as np
from PIL import Image, ImageEnhance
import multiprocessing
from resources.constants import RESAMPLE

try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.ANTIALIAS

class ImageProcessor:
    """Lớp xử lý hình ảnh cơ bản"""
    
    def __init__(self, logger=None):
        """Khởi tạo bộ xử lý hình ảnh"""
        from utils.logger import logger as default_logger
        self.logger = logger or default_logger
        self.num_cores = multiprocessing.cpu_count()
        
    def _apply_adjustments(self, img, brightness=1.0, contrast=1.0, saturation=1.0):
        """Áp dụng các điều chỉnh cho ảnh"""
        try:
            # Điều chỉnh độ sáng
            brightness = float(brightness)
            if brightness != 1.0:
                img = ImageEnhance.Brightness(img).enhance(brightness)
                
            # Điều chỉnh độ tương phản
            contrast = float(contrast)
            if contrast != 1.0:
                img = ImageEnhance.Contrast(img).enhance(contrast)
                
            # Điều chỉnh độ bão hòa
            saturation = float(saturation)
            if saturation != 1.0:
                img = ImageEnhance.Color(img).enhance(saturation)
                
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('adjustment_error')} - {e}")
            
        return img
        
    def remove_background(self, img, remove_black=False, remove_white=False):
        """Xử lý nền ảnh (loại bỏ màu đen hoặc trắng)"""
        try:
            if not (remove_black or remove_white):
                return img
                
            data = np.array(img)
            mask = np.zeros(data.shape[:2], bool)
            
            if remove_white:
                mask |= np.all(data[..., :3] == 255, axis=-1)
                
            if remove_black:
                mask |= np.all(data[..., :3] == 0, axis=-1)
                
            data[mask] = (0, 0, 0, 0)
            return Image.fromarray(data)
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('background_error')} - {e}")
            return img
            
    def resize_image(self, img, scale_ratio):
        """Thay đổi kích thước ảnh"""
        try:
            scale = float(scale_ratio)
            if scale > 0 and scale != 1.0:
                new_size = (int(img.width * scale), int(img.height * scale))
                img = img.resize(new_size, RESAMPLE)
                if self.logger:
                    self.logger.log(f"ℹ️ {self._('info_prefix')}: {self._('resized')} {new_size[0]}x{new_size[1]}")
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('resize_error')} - {e}")
        return img
        
    def process_image(self, image_path, output_folder, output_format=None, 
                      scale_ratio=None, remove_black=False, remove_white=False,
                      brightness=None, contrast=None, saturation=None, **kwargs):
        """
        Xử lý ảnh với các tùy chọn cơ bản
        
        Tham số:
            image_path (str): Đường dẫn đến ảnh cần xử lý
            output_folder (str): Thư mục lưu ảnh đầu ra
            output_format (str): Định dạng đầu ra (ví dụ: ".png", ".jpg")
            scale_ratio (float): Tỷ lệ thay đổi kích thước
            remove_black (bool): Xóa nền đen hay không
            remove_white (bool): Xóa nền trắng hay không
            brightness (float): Điều chỉnh độ sáng
            contrast (float): Điều chỉnh độ tương phản
            saturation (float): Điều chỉnh độ bão hòa
            **kwargs: Các tham số bổ sung, có thể là một đối tượng options
        """
        try:
            # Kiểm tra có đối tượng options được truyền vào hay không
            options = kwargs.get('options', None)
            
            # Nếu có options, sử dụng các giá trị từ options
            if options and isinstance(options, object):
                output_format = getattr(options, 'export_format', output_format)
                scale_ratio = getattr(options, 'scale_ratio', scale_ratio)
                remove_black = getattr(options, 'remove_black', remove_black)
                remove_white = getattr(options, 'remove_white', remove_white)
                brightness = getattr(options, 'brightness', brightness)
                contrast = getattr(options, 'contrast', contrast)
                saturation = getattr(options, 'saturation', saturation)
            
            # Thiết lập giá trị mặc định
            output_format = output_format or ".png"
            scale_ratio = scale_ratio or "1.0"
            brightness = brightness or "1.0"
            contrast = contrast or "1.0"
            saturation = saturation or "1.0"
            
            # Mở ảnh
            img = Image.open(image_path).convert("RGBA")
            
            # Áp dụng các điều chỉnh
            img = self._apply_adjustments(img, brightness, contrast, saturation)
            
            # Xử lý nền
            img = self.remove_background(img, remove_black, remove_white)
            
            # Thay đổi kích thước
            img = self.resize_image(img, scale_ratio)
            
            # Chuyển đổi sang RGB nếu định dạng đầu ra là JPG
            if output_format.lower() == ".jpg" or output_format.lower() == "jpg":
                img = img.convert("RGB")
                
            # Tạo tên file đầu ra
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            scale_prefix = f"{scale_ratio}x-" if float(scale_ratio) != 1.0 else ""
            
            # Đảm bảo định dạng đầu ra có dấu chấm
            if not output_format.startswith('.'):
                output_format = '.' + output_format
                
            output_path = os.path.join(output_folder, f"{scale_prefix}{base_name}{output_format}")
            
            # Lưu ảnh
            img.save(output_path)
            return output_path
            
        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('processing_error')} {os.path.basename(image_path)} - {e}")
            return None
            
    def batch_process(self, files, output_folder, **kwargs):
        """Xử lý hàng loạt ảnh"""
        if not files:
            if self.logger:
                self.logger.log(f"⚠️ {self._('warning_prefix')}: {self._('no_files_selected')}")
            return []
            
        start_time = time.time()
        processed_files = []
        total = len(files)
        
        if self.logger:
            self.logger.log(f"📊 {self._('info_prefix')}: {self._('total_images')} - {total}")
            
        for idx, path in enumerate(files, 1):
            try:
                output_path = self.process_image(path, output_folder, **kwargs)
                if output_path:
                    processed_files.append(output_path)
                    
                if self.logger:
                    pct = (idx / total) * 100
                    self.logger.log(f"✅ {self._('success_prefix')}: [{idx}/{total}] {self._('completed')} ({pct:.2f}%)")
            except Exception as e:
                if self.logger:
                    self.logger.log(f"❌ {self._('error_prefix')}: {self._('processing_error')} {os.path.basename(path)} - {e}")
                    
        # Thống kê thời gian
        elapsed = time.time() - start_time
        mins, secs = divmod(elapsed, 60)
        
        if self.logger:
            self.logger.log(f"🎉 {self._('success_prefix')}: {self._('all_completed')}")
            self.logger.log(f"⏱️ {self._('info_prefix')}: {self._('processing_time')} - {int(mins)} {self._('minutes')} {secs:.2f} {self._('seconds')}")
            
        return processed_files

    def process_batch(self, image_files, output_dir, options):
        """Xử lý hàng loạt ảnh sử dụng đa luồng"""
        if not image_files:
            return []
            
        # Tính toán số luồng phù hợp dựa trên số lượng ảnh và cores
        n_threads = min(self.num_cores, len(image_files))
        
        if n_threads > 1 and len(image_files) > 1:
            # Chia nhỏ công việc
            chunk_size = max(1, len(image_files) // n_threads)
            chunks = [image_files[i:i + chunk_size] for i in range(0, len(image_files), chunk_size)]
            
            # Sử dụng Pool để xử lý song song
            with multiprocessing.Pool(processes=n_threads) as pool:
                results = pool.starmap(
                    self._process_image_batch,
                    [(chunk, output_dir, options) for chunk in chunks]
                )
            
            # Kết hợp các kết quả
            processed_files = []
            for result in results:
                processed_files.extend(result)
            
            return processed_files
        else:
            # Xử lý tuần tự
            return self._process_image_batch(image_files, output_dir, options)
    
    def _process_image_batch(self, image_files, output_dir, options):
        """Xử lý một nhóm ảnh (được gọi bởi từng thread)"""
        processed_files = []
        
        for image_path in image_files:
            try:
                output_path = self.process_image(image_path, output_dir, options=options)
                if output_path:
                    processed_files.append(output_path)
            except Exception as e:
                self.logger.log(f"❌ {self._('error_prefix')}: {self._('processing_error')} {os.path.basename(image_path)} - {e}")
        
        return processed_files
    
    def _remove_background(self, img, is_black=True):
        """Loại bỏ nền đen hoặc trắng khỏi ảnh (tối ưu hóa)"""
        # Chuyển đổi thành RGBA nếu cần
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Chuyển sang numpy array để xử lý nhanh hơn
        data = np.array(img)
        
        # Tạo mặt nạ alpha dựa trên màu nền
        if is_black:
            # Tìm các pixel đen (R, G, B đều gần 0)
            mask = (data[:,:,0] < 10) & (data[:,:,1] < 10) & (data[:,:,2] < 10)
        else:
            # Tìm các pixel trắng (R, G, B đều gần 255)
            mask = (data[:,:,0] > 245) & (data[:,:,1] > 245) & (data[:,:,2] > 245)
        
        # Đặt alpha = 0 cho các pixel nền
        data[:,:,3][mask] = 0
        
        # Tạo ảnh mới từ mảng đã xử lý
        return Image.fromarray(data) 

    def adjust_image(self, image, brightness=1.0, contrast=1.0, saturation=1.0):
        """Điều chỉnh độ sáng, độ tương phản và độ bão hòa"""
        try:
            # Chuyển đổi về float để tính toán
            brightness = float(brightness)
            contrast = float(contrast)
            saturation = float(saturation)
            
            # Kiểm tra nếu không cần điều chỉnh
            if brightness == 1.0 and contrast == 1.0 and saturation == 1.0:
                return image
            
            # Tạo enhancer và áp dụng
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)
                
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast)
                
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(saturation)
                
            return image
        except Exception as e:
            self.logger.log(f"❌ {self._('error_prefix')}: {self._('adjustment_error')} - {e}")
            return image

    def batch_process_with_options(self, file_paths, output_dir, options=None):
        """
        Xử lý hàng loạt với các tùy chọn
        
        Tham số:
            file_paths (list): Danh sách đường dẫn ảnh cần xử lý
            output_dir (str): Thư mục đầu ra
            options (dict): Các tùy chọn xử lý
        """
        if options is None:
            options = {}
            
        try:
            return self.process_batch(file_paths, output_dir, **options)
        except Exception as e:
            self.logger.log(f"❌ {self._('error_prefix')}: {self._('processing_error')} {os.path.basename(image_path)} - {e}")
            return [] 