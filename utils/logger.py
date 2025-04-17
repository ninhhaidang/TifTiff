"""
Quản lý ghi nhật ký trong ứng dụng
"""

import os
import datetime
import threading
from enum import Enum
import queue

class LogLevel(Enum):
    """Cấp độ log"""
    DEBUG = 0
    INFO = 1
    SUCCESS = 2
    WARNING = 3
    ERROR = 4

class AsyncLogger:
    """Logger với khả năng xử lý bất đồng bộ để tăng hiệu suất"""
    
    def __init__(self, log_file=None, console_callback=None, max_queue_size=1000):
        """
        Khởi tạo logger
        
        Tham số:
            log_file (str): Đường dẫn đến file log (None để tắt ghi log ra file)
            console_callback (callable): Hàm callback để hiển thị log (None để tắt)
            max_queue_size (int): Kích thước tối đa của hàng đợi log
        """
        self.log_file = log_file
        self.console_callback = console_callback
        self.min_level = LogLevel.INFO
        self.log_queue = queue.Queue(maxsize=max_queue_size)
        self.log_listeners = []
        self.master = None
        self.status_var = None
        self.text_widget = None
        
        # Tạo thư mục chứa file log nếu cần
        if log_file:
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        
        # Khởi động worker thread
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.worker_thread.start()
    
    def set_text_widget(self, text_widget):
        """Đặt widget text để hiển thị log"""
        self.text_widget = text_widget
    
    def set_master(self, master):
        """Đặt cửa sổ chính của ứng dụng"""
        self.master = master
    
    def set_status_var(self, status_var):
        """Đặt biến trạng thái để cập nhật"""
        self.status_var = status_var
    
    def add_listener(self, listener):
        """Thêm listener để nhận thông báo khi có log mới"""
        if callable(listener) and listener not in self.log_listeners:
            self.log_listeners.append(listener)
    
    def remove_listener(self, listener):
        """Xóa listener"""
        if listener in self.log_listeners:
            self.log_listeners.remove(listener)
    
    def set_log_level(self, level):
        """Đặt cấp độ log tối thiểu"""
        if isinstance(level, LogLevel):
            self.min_level = level
        else:
            raise ValueError("Level phải là một LogLevel")
    
    def log(self, message, level=LogLevel.INFO, notify=True):
        """
        Ghi log
        
        Tham số:
            message (str): Nội dung log
            level (LogLevel): Cấp độ log
            notify (bool): Có thông báo cho listeners không
        """
        if level.value < self.min_level.value:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "notify": notify
        }
        
        try:
            self.log_queue.put(log_entry, block=False)
        except queue.Full:
            # Nếu queue đầy, ghi log ngay lập tức
            self._write_log(log_entry)
    
    def debug(self, message, notify=False):
        """Log level DEBUG"""
        self.log(message, LogLevel.DEBUG, notify)
    
    def info(self, message, notify=True):
        """Log level INFO"""
        self.log(message, LogLevel.INFO, notify)
    
    def success(self, message, notify=True):
        """Log level SUCCESS"""
        self.log(message, LogLevel.SUCCESS, notify)
    
    def warning(self, message, notify=True):
        """Log level WARNING"""
        self.log(message, LogLevel.WARNING, notify)
    
    def error(self, message, notify=True):
        """Log level ERROR"""
        self.log(message, LogLevel.ERROR, notify)
    
    def _process_log_queue(self):
        """Thread chạy ngầm để xử lý hàng đợi log"""
        while self.running:
            try:
                log_entry = self.log_queue.get(block=True, timeout=0.5)
                self._write_log(log_entry)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                # Đảm bảo thread không bị crash
                print(f"Lỗi trong log thread: {str(e)}")
    
    def _write_log(self, log_entry):
        """Xử lý một mục log"""
        timestamp = log_entry["timestamp"]
        level = log_entry["level"]
        message = log_entry["message"]
        notify = log_entry["notify"]
        
        # Định dạng thông điệp log
        level_str = level.name
        formatted_log = f"[{timestamp}] {level_str}: {message}"
        
        # Ghi ra file nếu được cấu hình
        if self.log_file:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(formatted_log + "\n")
            except Exception as e:
                print(f"Không thể ghi log ra file: {str(e)}")
        
        # Gửi đến callback hiển thị nếu có
        if self.console_callback and callable(self.console_callback):
            try:
                self.console_callback(formatted_log, level)
            except Exception as e:
                print(f"Lỗi trong callback hiển thị log: {str(e)}")
        
        # Hiển thị trong text widget nếu có
        if self.text_widget:
            try:
                # Sử dụng màu khác nhau cho các cấp độ log
                tag_map = {
                    LogLevel.DEBUG: "debug",
                    LogLevel.INFO: "info",
                    LogLevel.SUCCESS: "success",
                    LogLevel.WARNING: "warning",
                    LogLevel.ERROR: "error"
                }
                
                # Định nghĩa màu cho các tag nếu chưa có
                try:
                    if tag_map[level] not in self.text_widget.tag_names():
                        color_map = {
                            "debug": "#808080",  # Xám
                            "info": "#000000",   # Đen
                            "success": "#008800", # Xanh lá
                            "warning": "#FF8800", # Cam
                            "error": "#FF0000"   # Đỏ
                        }
                        self.text_widget.tag_configure(tag_map[level], foreground=color_map[tag_map[level]])
                except Exception:
                    pass
                
                # Thêm log vào cuối và tự động cuộn
                self.text_widget.insert("end", formatted_log + "\n", tag_map[level])
                self.text_widget.see("end")
            except Exception as e:
                print(f"Lỗi khi hiển thị log trong UI: {str(e)}")
                
        # Cập nhật trạng thái nếu có
        if self.status_var and level.value >= LogLevel.WARNING.value:
            try:
                self.status_var.set(message)
            except Exception as e:
                print(f"Lỗi khi cập nhật trạng thái: {str(e)}")
        
        # Thông báo cho các listeners
        if notify:
            for listener in self.log_listeners:
                try:
                    listener(message, level)
                except Exception as e:
                    print(f"Lỗi trong log listener: {str(e)}")
    
    def shutdown(self):
        """Đóng logger an toàn, đảm bảo tất cả logs được ghi"""
        self.running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        
        # Xử lý các log còn lại trong queue
        while not self.log_queue.empty():
            try:
                log_entry = self.log_queue.get(block=False)
                self._write_log(log_entry)
                self.log_queue.task_done()
            except queue.Empty:
                break

# Tạo một instance của logger
logger = AsyncLogger()

# Hàm wrapper tiện lợi cho các module khác sử dụng
def log(message, level=LogLevel.INFO, notify=True):
    """Log message với level mặc định là INFO"""
    logger.log(message, level, notify)

def setup_logger(log_file=None, console_callback=None):
    """Thiết lập logger toàn cục"""
    global logger
    logger = AsyncLogger(log_file, console_callback)
    return logger 