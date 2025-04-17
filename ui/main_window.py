"""
Cửa sổ chính của ứng dụng TifTiff
"""

import os
import threading
import tkinter as tk
from tkinter import StringVar, BooleanVar, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES

from ui.tabs.basic_tab import BasicTab
from ui.tabs.geo_tab import GeoTab
from ui.tabs.adjust_tab import AdjustTab
from ui.tabs.options_tab import OptionsTab
from ui.tabs.log_tab import LogTab

from resources.constants import ICONS, resource_path, COMMON_CRS
from resources.translations import get_translation
from utils.config import config_manager, get_config, set_config
from utils.logger import logger
from processing.image_processor import ImageProcessor
from processing.geo_processor import GeoProcessor
from processing.metadata_processor import MetadataProcessor

class MainWindow:
    """Cửa sổ chính của ứng dụng"""
    
    def __init__(self, master):
        """Khởi tạo cửa sổ chính"""
        self.master = master
        
        # Định nghĩa font
        self.bold_font = ("Segoe UI", 10, "bold")
        self.normal_font = ("Segoe UI", 10)
        self.small_font = ("Segoe UI", 9)
        self.header_font = ("Segoe UI", 11, "bold")
        
        # Biến dữ liệu
        self.input_folder = ""
        self.output_folder = ""
        self.input_files = []
        self.current_image = None
        self.current_image_path = ""
        
        # Các biến cài đặt cơ bản
        self.input_path_var = StringVar()
        self.output_path_var = StringVar()
        self.remove_white_bg = BooleanVar(value=False)
        self.remove_black_bg = BooleanVar(value=False)
        self.output_format_var = StringVar(value=".png")
        self.scale_ratio_var = StringVar(value="1.0")
        
        # Thêm biến cho chức năng chuyển đổi hệ tọa độ
        self.enable_reproject = BooleanVar(value=False)
        self.source_crs_var = StringVar(value="")
        self.target_crs_var = StringVar(value="EPSG:4326")
        self.detected_crs_var = StringVar(value="")
        
        # Thêm biến cho việc xuất ảnh với hệ tọa độ
        self.preserve_geospatial = BooleanVar(value=True)
        self.geo_format_var = StringVar(value="GeoTIFF (.tif)")
        
        # Thêm biến cho điều chỉnh ảnh
        self.brightness_var = StringVar(value="1.0")
        self.contrast_var = StringVar(value="1.0")
        self.saturation_var = StringVar(value="1.0")
        
        # Biến giao diện
        self.theme_var = StringVar(value="cosmo")
        self.language_var = StringVar(value="en")
        self.is_dark_mode = BooleanVar(value=False)
        
        # Thêm biến để theo dõi trạng thái khởi tạo UI
        self.ui_initialized = False
        
        # Biến trạng thái
        self.status_var = StringVar(value="")
        self.is_processing = False
        
        # Khởi tạo logger
        self.logger = logger
        self.logger.set_master(self.master)
        self.logger.set_status_var(self.status_var)
        
        # Khởi tạo các processor
        self.image_processor = ImageProcessor(self.logger)
        self.geo_processor = GeoProcessor(self.logger)
        self.metadata_processor = MetadataProcessor(self.logger)
        
        # Nạp cấu hình
        self._load_config()
        
        # Chuẩn bị giao diện
        self._configure_master()
        
        # Tạo UI
        self._build_ui()
        
        # Đánh dấu UI đã được khởi tạo
        self.ui_initialized = True
        
        # Cập nhật trạng thái UI sau khi đã khởi tạo
        self._update_geo_options()
        self.status_var.set(self._("ready"))
        
    def _(self, key):
        """Hàm dịch ngôn ngữ dựa trên khóa"""
        return get_translation(key, self.language_var.get())
        
    def _configure_master(self):
        """Thiết lập cửa sổ chính"""
        # Áp dụng chủ đề
        self.style = ttk.Style(self.theme_var.get())
        
        # Cấu hình cửa sổ
        self.master.title(self._("app_title"))
        self.master.geometry("850x700")
        self.master.iconbitmap(resource_path("icon.ico"))
        
        # Tự động cập nhật chủ đề khi thay đổi
        self.theme_var.trace_add("write", self._update_theme)
        self.language_var.trace_add("write", self._update_language)
        
    def _tab_icon_key(self, idx):
        """Trả về key icon cho tab dựa vào index"""
        icons = {
            0: "input",
            1: "geo",
            2: "adjust",
            3: "options",
            4: "info"
        }
        return icons.get(idx, "info")
        
    def _build_ui(self):
        """Xây dựng giao diện người dùng chính"""
        # Tạo frame chính
        main_frame = ttk.Frame(self.master, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Tạo notebook để chứa các tab
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab chính: Cơ bản
        basic_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(basic_tab, text=f"{ICONS['input']} {self._('basic_tab')}")
        
        # Tab nâng cao: Chuyển đổi hệ tọa độ
        geo_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(geo_tab, text=f"{ICONS['geo']} {self._('geo_tab')}")
        
        # Tab điều chỉnh ảnh
        adjust_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(adjust_tab, text=f"{ICONS['adjust']} {self._('advanced_tab')}")
        
        # Tab tùy chọn
        options_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(options_tab, text=f"{ICONS['options']} {self._('options_tab')}")
        
        # Tab nhật ký
        log_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(log_tab, text=f"{ICONS['info']} {self._('log_tab')}")
        
        # Xây dựng các tab
        self.basic_tab = BasicTab(basic_tab, self)
        self.geo_tab = GeoTab(geo_tab, self)
        self.adjust_tab = AdjustTab(adjust_tab, self)
        self.options_tab = OptionsTab(options_tab, self)
        self.log_tab = LogTab(log_tab, self)
        
        # Phần dưới: Tiến trình và nút bắt đầu
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="x", pady=(10, 0))
        
        # Tiến trình
        progress_frame = ttk.LabelFrame(bottom_frame, text=f"{ICONS['progress']} {self._('progress')}", padding=10)
        progress_frame.pack(fill="x", pady=(0, 10))
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", length=500)
        self.progress.pack(fill="x", pady=(5, 10))
        
        # Nút bắt đầu
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill="x")
        
        self.start_button = ttk.Button(
            button_frame,
            text=f"{ICONS['convert']} {self._('start_processing')}",
            command=self.start_conversion,
            style="success.TButton",
            width=20,
            bootstyle=SUCCESS
        )
        self.start_button.pack(side="right", padx=5)
        
        # Thanh trạng thái
        status_bar = ttk.Frame(main_frame, bootstyle="secondary")
        status_bar.pack(fill="x", side="bottom", pady=(10, 0))
        
        ttk.Label(status_bar, textvariable=self.status_var, font=self.small_font, padding=5).pack(side="left")
        
    def _update_theme(self, *args):
        """Cập nhật chủ đề khi người dùng thay đổi"""
        theme = self.theme_var.get()
        self.style = ttk.Style(theme)
        
        # Kiểm tra xem đây có phải là chủ đề tối không
        is_dark = theme in ["darkly", "superhero", "solar"]
        self.is_dark_mode.set(is_dark)
        
        # Cập nhật màu log text nếu tab log đã được khởi tạo
        if hasattr(self, 'log_tab') and hasattr(self.log_tab, 'log_text'):
            bg_color = "#f7f7f7" if not is_dark else "#2a2a2a"
            fg_color = "#000000" if not is_dark else "#ffffff"
            self.log_tab.log_text.config(bg=bg_color, fg=fg_color)
            
        # Lưu cấu hình
        self._save_config()
        
    def _update_language(self, *args):
        """Cập nhật ngôn ngữ khi người dùng thay đổi"""
        if not self.ui_initialized:
            return
            
        # Cập nhật tiêu đề cửa sổ
        self.master.title(self._("app_title"))
        
        # Cập nhật tên các tab
        if hasattr(self, 'notebook'):
            tabs = {
                0: self._("basic_tab"),
                1: self._("geo_tab"),
                2: self._("advanced_tab"),
                3: self._("options_tab"),
                4: self._("log_tab")
            }
            
            for idx, text in tabs.items():
                if idx < self.notebook.index('end'):
                    self.notebook.tab(idx, text=f"{ICONS.get(self._tab_icon_key(idx), '📄')} {text}")
                    
        # Lưu cấu hình
        self._save_config()
        
    def _update_geo_options(self):
        """Cập nhật trạng thái các tùy chọn xuất ảnh địa lý dựa vào việc bật/tắt chuyển đổi hệ tọa độ"""
        # Kiểm tra xem UI đã được khởi tạo chưa
        if not hasattr(self, 'ui_initialized') or not self.ui_initialized:
            return
            
        if not hasattr(self, 'preserve_geo_check') or not hasattr(self, 'geo_format_menu'):
            return
            
        if self.enable_reproject.get():
            self.preserve_geo_check["state"] = "normal"
            if self.preserve_geospatial.get():
                self.geo_format_menu["state"] = "normal"
            else:
                self.geo_format_menu["state"] = "disabled"
        else:
            self.preserve_geo_check["state"] = "disabled"
            self.geo_format_menu["state"] = "disabled"
            
        # Cập nhật UI
        self.master.update()
        
    def _load_config(self):
        """Nạp cấu hình từ file"""
        # Cài đặt cơ bản
        self.remove_white_bg.set(get_config("remove_white_bg", False))
        self.remove_black_bg.set(get_config("remove_black_bg", False))
        self.input_folder = get_config("last_input", "")
        self.output_folder = get_config("last_output", "")
        self.input_path_var.set(self.input_folder)
        self.output_path_var.set(self.output_folder)
        self.output_format_var.set(get_config("output_format", ".png"))
        self.scale_ratio_var.set(get_config("scale_ratio", "1.0"))
        
        # Cài đặt hệ tọa độ
        self.enable_reproject.set(get_config("enable_reproject", False))
        self.target_crs_var.set(get_config("target_crs", "EPSG:4326"))
        self.preserve_geospatial.set(get_config("preserve_geospatial", True))
        self.geo_format_var.set(get_config("geo_format", "GeoTIFF (.tif)"))
        
        # Cài đặt điều chỉnh ảnh
        self.brightness_var.set(get_config("brightness", "1.0"))
        self.contrast_var.set(get_config("contrast", "1.0"))
        self.saturation_var.set(get_config("saturation", "1.0"))
        
        # Cài đặt giao diện
        self.theme_var.set(get_config("theme", "cosmo"))
        self.language_var.set(get_config("language", "en"))
        
    def _save_config(self):
        """Lưu cấu hình vào file"""
        config = {
            # Cài đặt cơ bản
            "remove_white_bg": self.remove_white_bg.get(),
            "remove_black_bg": self.remove_black_bg.get(),
            "last_input": self.input_folder,
            "last_output": self.output_folder,
            "output_format": self.output_format_var.get(),
            "scale_ratio": self.scale_ratio_var.get(),
            
            # Cài đặt hệ tọa độ
            "enable_reproject": self.enable_reproject.get(),
            "target_crs": self.target_crs_var.get(),
            "preserve_geospatial": self.preserve_geospatial.get(),
            "geo_format": self.geo_format_var.get(),
            
            # Cài đặt điều chỉnh ảnh
            "brightness": self.brightness_var.get(),
            "contrast": self.contrast_var.get(),
            "saturation": self.saturation_var.get(),
            
            # Cài đặt giao diện
            "theme": self.theme_var.get(),
            "language": self.language_var.get()
        }
        config_manager.update(config)
        
    def browse_input(self):
        """Chọn file ảnh đầu vào"""
        paths = filedialog.askopenfilenames(title="Chọn ảnh nguồn", filetypes=[("Images", "*.tif *.tiff *.png *.jpg *.jpeg *.bmp")])
        if paths:
            self.input_files = list(paths)
            self.input_folder = os.path.dirname(paths[0])
            self.input_path_var.set(" ; ".join(os.path.basename(f) for f in paths))
            self.logger.log(f"{ICONS['input']} {self._('selected_files')}: {len(paths)}")
            
            # Tự động phát hiện hệ tọa độ sau khi chọn file
            if any(p.lower().endswith(('.tif', '.tiff')) for p in paths):
                self.detect_crs()
        
    def browse_input_folder(self):
        """Chọn thư mục ảnh đầu vào"""
        folder = filedialog.askdirectory(title="Chọn thư mục ảnh nguồn")
        if folder:
            self.input_folder = folder
            self.input_files = []
            self.input_path_var.set(folder)
            self.logger.log(f"{ICONS['input']} {self._('selected_folder')}: {folder}")
            
            # Kiểm tra xem có file tif/tiff trong thư mục không
            if any(f.lower().endswith(('.tif', '.tiff')) for f in os.listdir(folder)):
                self.detect_crs()
                
    def browse_output(self):
        """Chọn thư mục đầu ra"""
        folder = filedialog.askdirectory(title="Chọn thư mục lưu ảnh")
        if folder:
            self.output_folder = folder
            self.output_path_var.set(folder)
            self.logger.log(f"{ICONS['output']} {self._('selected_output')}: {folder}")
            
    def handle_drop_input(self, event):
        """Xử lý kéo thả file/thư mục đầu vào"""
        dropped = self.master.tk.splitlist(event.data)
        self.input_files = []
        folder_dropped = None
        for path in dropped:
            if os.path.isdir(path):
                folder_dropped = path
                self.logger.log(f"{ICONS['input']} {self._('dropped_folder')}: {path}")
            elif os.path.isfile(path):
                self.input_files.append(path)
        if self.input_files:
            self.input_path_var.set(" ; ".join(os.path.basename(f) for f in self.input_files))
            self.logger.log(f"{ICONS['input']} {self._('dropped_files')}: {len(self.input_files)}")
            # Kiểm tra xem có file tif/tiff nào được kéo thả không
            if any(f.lower().endswith(('.tif', '.tiff')) for f in self.input_files):
                self.detect_crs()
        elif folder_dropped:
            self.input_folder = folder_dropped
            self.input_path_var.set(folder_dropped)
            # Kiểm tra xem có file tif/tiff trong thư mục không
            if any(f.lower().endswith(('.tif', '.tiff')) for f in os.listdir(folder_dropped)):
                self.detect_crs()
                
    def handle_drop_output(self, event):
        """Xử lý kéo thả thư mục đầu ra"""
        dropped = self.master.tk.splitlist(event.data)
        for path in dropped:
            if os.path.isdir(path):
                self.output_folder = path
                self.output_path_var.set(path)
                self.logger.log(f"{ICONS['output']} {self._('dropped_output')}: {path}")
                
    def detect_crs(self):
        """Phát hiện và hiển thị hệ tọa độ của ảnh đã chọn"""
        # Reset
        self.detected_crs_var.set(self._("no_crs_info"))
        
        # Kiểm tra xem có file nào được chọn không
        if not self.input_files:
            self.logger.log(self._("no_files_selected"))
            return
            
        # Lọc ra các file TIF/TIFF
        tif_files = [f for f in self.input_files if f.lower().endswith(('.tif', '.tiff'))]
        
        if not tif_files:
            self.logger.log(self._("no_tiff_found"))
            self.detected_crs_var.set(self._("no_tiff_found"))
            return
            
        # Phát hiện CRS từ file đầu tiên
        result = self.geo_processor.detect_crs(tif_files[0])
        
        if result:
            self.logger.log(f"{self._('detected_crs')} {result}")
            self.detected_crs_var.set(str(result))
        else:
            self.logger.log(self._("no_crs_info"))
            self.detected_crs_var.set(self._("no_crs_info"))
            
    def export_metadata(self, format_type):
        """Xuất metadata từ các ảnh được chọn"""
        if not self.input_files and not self.input_folder:
            self.logger.log(f"{ICONS['warning']} {self._('no_files_selected')}")
            return
            
        # Xác định danh sách file cần xử lý
        files = self.input_files or [
            os.path.join(self.input_folder, f)
            for f in os.listdir(self.input_folder)
            if f.lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg', '.bmp'))
        ]
        
        if not files:
            self.logger.log(f"{ICONS['warning']} {self._('no_tiff_found')}")
            return
            
        # Xác định nơi lưu file metadata
        if not self.output_folder:
            self.logger.log(f"{ICONS['warning']} {self._('no_output_selected')}")
            return
            
        # Sử dụng MetadataProcessor để xuất metadata
        self.metadata_processor.export_metadata(files, self.output_folder, format_type)
        
    def start_conversion(self):
        """Bắt đầu quá trình chuyển đổi ảnh"""
        if not self.input_folder and not self.input_files:
            self.logger.log(f"{ICONS['warning']} {self._('no_input_selected')}")
            return
            
        if not self.output_folder:
            self.logger.log(f"{ICONS['warning']} {self._('no_output_selected')}")
            return

        self._save_config()
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Sử dụng luồng riêng để không treo giao diện
        thread = threading.Thread(target=self._process_images, daemon=True)
        thread.start()
        
    def _process_images(self):
        """Xử lý chuyển đổi ảnh"""
        # Đánh dấu đang xử lý
        self.is_processing = True
        self.status_var.set(self._("processing"))
        
        # Xác định danh sách file cần xử lý
        files = self.input_files or [
            os.path.join(self.input_folder, f)
            for f in os.listdir(self.input_folder)
            if f.lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg', '.bmp'))
        ]
        
        # Thiết lập thanh tiến trình
        total = len(files)
        self.progress["maximum"] = total
        self.logger.log(f"📊 {self._('total_images')}: {total}")
        
        # Xử lý từng file
        processed_files = []
        for idx, path in enumerate(files, 1):
            # Cập nhật thanh tiến trình
            self.progress["value"] = idx
            self.master.update_idletasks()
            
            try:
                # Nếu cần chuyển đổi hệ tọa độ
                geo_metadata = None
                if self.enable_reproject.get() and path.lower().endswith(('.tif', '.tiff')):
                    try:
                        # Lấy hệ tọa độ đích
                        dst_crs = ""
                        for name, code in COMMON_CRS.items():
                            if name == self.target_crs_var.get():
                                dst_crs = code
                                break
                                
                        # Chuyển đổi hệ tọa độ
                        if dst_crs and self.preserve_geospatial.get():
                            # Nếu cần lưu thông tin địa lý, lấy metadata
                            geo_metadata = self.geo_processor.extract_geo_metadata(
                                path, 
                                dst_crs, 
                                None if self.source_crs_var.get() == "Tự động phát hiện" else COMMON_CRS[self.source_crs_var.get()]
                            )
                    except Exception as e:
                        self.logger.log(f"⚠️ {self._('error_prefix')}: {e}")
                        self.logger.log(f"⚠️ {self._('continue_with_original')}")
                        
                # Xử lý ảnh
                img_options = {
                    'output_format': self.output_format_var.get(),
                    'scale_ratio': self.scale_ratio_var.get(),
                    'remove_black': self.remove_black_bg.get(),
                    'remove_white': self.remove_white_bg.get(),
                    'brightness': self.brightness_var.get(),
                    'contrast': self.contrast_var.get(),
                    'saturation': self.saturation_var.get()
                }
                
                # Xử lý ảnh bình thường (không lưu thông tin địa lý)
                if not (self.enable_reproject.get() and self.preserve_geospatial.get() and geo_metadata):
                    # Xử lý ảnh thông thường
                    output_path = self.image_processor.process_image(path, self.output_folder, **img_options)
                    if output_path:
                        processed_files.append(output_path)
                else:
                    # Xử lý ảnh với thông tin địa lý
                    # 1. Mở và xử lý ảnh
                    output_path = self.image_processor.process_image(path, self.output_folder, **img_options)
                    
                    # 2. Nếu có metadata địa lý, lưu lại với thông tin địa lý
                    if geo_metadata and output_path:
                        # Cập nhật metadata nếu có thay đổi kích thước
                        if float(self.scale_ratio_var.get()) != 1.0:
                            geo_metadata = self.geo_processor.update_geo_metadata_scale(
                                geo_metadata, 
                                float(self.scale_ratio_var.get())
                            )
                            
                        # Lưu với thông tin địa lý
                        from PIL import Image
                        img = Image.open(output_path)
                        
                        # Chọn phần mở rộng dựa trên định dạng
                        geo_ext = ".tif"
                        if self.geo_format_var.get() == "GeoJPEG2000 (.jp2)":
                            geo_ext = ".jp2"
                        elif self.geo_format_var.get() == "ERDAS Imagine (.img)":
                            geo_ext = ".img"
                        
                        # Đổi tên file theo định dạng địa lý
                        geo_output_path = os.path.splitext(output_path)[0] + geo_ext
                        
                        # Lưu ảnh với thông tin địa lý
                        self.geo_processor.save_with_geospatial(img, geo_output_path, geo_metadata)
                        
                        # Xóa file tạm
                        try:
                            os.remove(output_path)
                        except:
                            pass
                            
                        processed_files.append(geo_output_path)
                        
                # Cập nhật giao diện và log
                pct = (idx / total) * 100
                self.logger.log(f"✅ [{idx}/{total}] {self._('completed')} ({pct:.2f}%)")
                
            except Exception as e:
                self.logger.log(f"❌ {self._('error_prefix')} {os.path.basename(path)}: {e}")
        
        # Hoàn tất
        self.logger.log(f"🎉 {self._('all_completed')}")
        self.status_var.set(self._("completed"))
        self.is_processing = False 