"""
Cửa sổ chính của ứng dụng TifTiff
"""

import os
import threading
import tkinter as tk
from tkinter import StringVar, BooleanVar, filedialog, Menu
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinterdnd2 import DND_FILES
import rasterio
import numpy as np

from ui.tabs.basic_tab import BasicTab
from ui.tabs.geo_tab import GeoTab
from ui.tabs.adjust_tab import AdjustTab
from ui.tabs.options_tab import OptionsTab
from ui.tabs.log_tab import LogTab
from ui.tabs.coordinate_tab import CoordinateTab

from resources.constants import ICONS, resource_path, COMMON_CRS, THEMES, LANGUAGES
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
        self.bold_font = ("Segoe UI", 9, "bold")
        self.normal_font = ("Segoe UI", 9)
        self.small_font = ("Segoe UI", 8)
        self.header_font = ("Segoe UI", 10, "bold")
        
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
        
        # Biến chọn chế độ xử lý
        self.mode_var = StringVar(value="presentation")
        
        # Lưu trữ cài đặt riêng cho từng mode để tránh xung đột
        self.presentation_settings = {
            'output_format': '.png',
            'remove_white_bg': False,
            'remove_black_bg': False,
            'brightness': '1.0',
            'contrast': '1.0',
            'saturation': '1.0',
            'scale_ratio': '1.0'
        }
        
        self.research_settings = {
            'output_format': '.tif',
            'remove_white_bg': False,
            'remove_black_bg': False,
            'brightness': '1.0',
            'contrast': '1.0',
            'saturation': '1.0',
            'scale_ratio': '1.0',
            'preserve_geospatial': True,
            'geo_format': 'GeoTIFF (.tif)'
        }
        
        # Thêm biến để theo dõi trạng thái khởi tạo UI
        self.ui_initialized = False
        
        # Biến trạng thái
        self.status_var = StringVar(value="")
        self.is_processing = False
        
        # Khởi tạo logger
        self.logger = logger
        self.logger.set_master(self.master)
        self.logger.set_status_var(self.status_var)
        
        # Cập nhật logger để sử dụng log_text trực tiếp
        def log_callback(message, level=None):
            if hasattr(self, 'log_text'):
                self.log_text.config(state="normal")
                self.log_text.insert("end", message + "\n")
                self.log_text.see("end")
                self.log_text.config(state="disabled")
                
        self.logger.set_log_callback(log_callback)
        
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
        self.master.geometry("900x900")  # Tăng chiều cao cửa sổ để hiển thị đầy đủ
        self.master.minsize(800, 800)  # Tăng kích thước tối thiểu theo chiều cao
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
        # Thiết lập style và padding toàn cục
        padx, pady = 8, 6
        
        # Tạo frame chính
        main_frame = ttk.Frame(self.master, padding=5)
        main_frame.pack(fill="both", expand=True)
        
        # Tạo tab chính để phân chia theo mục đích sử dụng
        self.main_notebook = ttk.Notebook(main_frame, style="primary.TNotebook")
        self.main_notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Tạo 2 tab chính: Xử lý ảnh cho báo cáo và Xử lý ảnh cho nghiên cứu
        self.presentation_tab = ttk.Frame(self.main_notebook, padding=5)
        self.research_tab = ttk.Frame(self.main_notebook, padding=5)
        
        # Thêm 2 tab vào notebook chính
        self.main_notebook.add(self.presentation_tab, text=f"{ICONS['presentation']} {self._('presentation_mode')}")
        self.main_notebook.add(self.research_tab, text=f"{ICONS['research']} {self._('research_mode')}")
        
        # Thêm sự kiện cho việc chuyển tab
        self.main_notebook.bind("<<NotebookTabChanged>>", self._on_main_tab_changed)
        
        # Tạo các notebook cho từng tab
        # Notebook cho mode xử lý ảnh báo cáo, slide
        self.presentation_notebook = ttk.Notebook(self.presentation_tab, style="secondary.TNotebook")
        self.presentation_notebook.pack(fill="both", expand=True, padx=padx, pady=pady)
        
        # Tab cơ bản cho báo cáo, slide
        basic_tab = ttk.Frame(self.presentation_notebook, padding=10) 
        self.presentation_notebook.add(basic_tab, text=f"{ICONS['input']} {self._('input_output_tab')}")
        
        # Tab điều chỉnh ảnh cho báo cáo, slide
        adjust_tab = ttk.Frame(self.presentation_notebook, padding=10)
        self.presentation_notebook.add(adjust_tab, text=f"{ICONS['adjust']} {self._('image_adjustment_tab')}")
        
        # Notebook cho mode xử lý ảnh nghiên cứu, tính toán
        self.research_notebook = ttk.Notebook(self.research_tab, style="secondary.TNotebook")
        self.research_notebook.pack(fill="both", expand=True, padx=padx, pady=pady)
        
        # Tab cơ bản cho nghiên cứu (chọn ảnh, lưu ảnh)
        research_basic_tab = ttk.Frame(self.research_notebook, padding=10)
        self.research_notebook.add(research_basic_tab, text=f"{ICONS['input']} {self._('input_output_tab')}")
        
        # Tab chuyển đổi hệ tọa độ
        geo_tab = ttk.Frame(self.research_notebook, padding=10)
        self.research_notebook.add(geo_tab, text=f"{ICONS['geo']} {self._('geo_tab')}")
        
        # Tab tùy chọn cho nghiên cứu
        research_options_tab = ttk.Frame(self.research_notebook, padding=10)
        self.research_notebook.add(research_options_tab, text=f"{ICONS['options']} {self._('metadata_tab')}")
        
        # Xây dựng các tab
        self.basic_tab = BasicTab(basic_tab, self)
        self.research_basic_tab = ResearchBasicTab(research_basic_tab, self)
        self.geo_tab = GeoTab(geo_tab, self)
        self.adjust_tab = AdjustTab(adjust_tab, self)
        self.research_options_tab = ResearchOptionsTab(research_options_tab, self)
        
        # Tạo phần giao diện ở dưới cùng
        bottom_container = ttk.Frame(main_frame)
        bottom_container.pack(fill="x", expand=False, pady=(5, 0))
        
        # Chia thành 2 phần: log bên trái và tiến trình/nút bên phải
        left_pane = ttk.Frame(bottom_container)
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        right_pane = ttk.Frame(bottom_container)
        right_pane.pack(side="right", fill="y", expand=False, padx=(5, 0))
        
        # Log panel - hiển thị ở tất cả các mode (bên trái)
        self.log_frame = ttk.LabelFrame(left_pane, text=f"{ICONS['info']} {self._('log_tab')}", padding=5)
        self.log_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        # Tạo text widget cho log với thanh cuộn
        log_container = ttk.Frame(self.log_frame)
        log_container.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(
            log_container,
            height=4,  # Giảm chiều cao của log để tối ưu không gian hiển thị
            wrap="word",
            font=self.small_font
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        
        # Thanh cuộn cho log
        log_scrollbar = ttk.Scrollbar(log_container, command=self.log_text.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        # Thiết lập màu sắc ban đầu cho log
        bg_color = "#f7f7f7" if not self.is_dark_mode.get() else "#2a2a2a"
        fg_color = "#000000" if not self.is_dark_mode.get() else "#ffffff"
        self.log_text.config(bg=bg_color, fg=fg_color)
        
        # Phần tiến trình và nút bắt đầu (bên phải)
        # Tiến trình
        self.progress_frame = ttk.LabelFrame(right_pane, text=f"{ICONS['progress']} {self._('progress')}", padding=5)
        self.progress_frame.pack(fill="x", pady=(0, 8))
        
        self.progress = ttk.Progressbar(
            self.progress_frame, 
            orient="horizontal", 
            mode="determinate", 
            length=200,  # Giảm kích thước thanh tiến trình
            bootstyle="success-striped"
        )
        self.progress.pack(fill="x", pady=(3, 3))
        
        # Nút điều khiển
        control_frame = ttk.Frame(right_pane)
        control_frame.pack(fill="x", pady=(0, 5))
        
        # Nút bắt đầu
        self.start_button = ttk.Button(
            control_frame,
            text=f"{ICONS['convert']} {self._('start_processing')}",
            command=self.start_conversion,
            style="success.TButton",
            width=18,  # Giảm kích thước chiều rộng button
            bootstyle=SUCCESS
        )
        self.start_button.pack(pady=(0, 8), fill="x")
        
        # Nút cài đặt
        self.settings_button = ttk.Button(
            control_frame,
            text=f"{ICONS['settings']} {self._('settings_button')}",
            command=self._open_settings_dialog,
            bootstyle=SECONDARY,
            width=18  # Giảm kích thước chiều rộng button
        )
        self.settings_button.pack(pady=(0, 8), fill="x")
        
        # Nút trợ giúp
        self.help_button = ttk.Button(
            control_frame,
            text=f"{ICONS['help']} {self._('help_button')}",
            command=self._show_about,
            bootstyle=INFO,
            width=18  # Giảm kích thước chiều rộng button
        )
        self.help_button.pack(fill="x", pady=(0, 5))
        
        # Thanh trạng thái
        status_bar = ttk.Frame(main_frame, bootstyle="secondary")
        status_bar.pack(fill="x", side="bottom", pady=(5, 0))
        
        # Thông tin phiên bản bên phải
        version_label = ttk.Label(
            status_bar,
            text="TifTiff v1.1.0",
            font=self.small_font,
            foreground="#888888"
        )
        version_label.pack(side="right", padx=5)
        
        # Trạng thái bên trái
        status_label = ttk.Label(
            status_bar, 
            textvariable=self.status_var, 
            font=self.small_font, 
            padding=5
        )
        status_label.pack(side="left")
        
        # Khởi tạo các cài đặt mặc định cho từng mode
        self._init_mode_settings()
        
        # Thiết lập chế độ mặc định
        self._on_main_tab_changed(None)
        
    def _on_main_tab_changed(self, event):
        """Xử lý khi người dùng chuyển tab chính"""
        if not hasattr(self, 'main_notebook'):
            return
            
        current_tab = self.main_notebook.index('current')
        # 0 = presentation tab, 1 = research tab
        if current_tab == 0:
            self.mode_var.set("presentation")
        else:
            self.mode_var.set("research")
            
        # Cập nhật cài đặt theo chế độ mới
        self._update_mode()
        
    def _update_mode(self):
        """Cập nhật giao diện theo chế độ xử lý được chọn"""
        # Lưu cài đặt hiện tại của mode trước đó
        previous_mode = "presentation" if self.mode_var.get() == "research" else "research"
        if previous_mode == "presentation":
            # Lưu các cài đặt của chế độ presentation
            self.presentation_settings = {
                'output_format': self.output_format_var.get(),
                'remove_white_bg': self.remove_white_bg.get(),
                'remove_black_bg': self.remove_black_bg.get(),
                'brightness': self.brightness_var.get(),
                'contrast': self.contrast_var.get(),
                'saturation': self.saturation_var.get(),
                'scale_ratio': self.scale_ratio_var.get()
            }
        else:
            # Lưu các cài đặt của chế độ research
            self.research_settings = {
                'output_format': self.output_format_var.get(),
                'remove_white_bg': self.remove_white_bg.get(),
                'remove_black_bg': self.remove_black_bg.get(),
                'brightness': self.brightness_var.get(),
                'contrast': self.contrast_var.get(),
                'saturation': self.saturation_var.get(),
                'scale_ratio': self.scale_ratio_var.get(),
                'preserve_geospatial': self.preserve_geospatial.get(),
                'geo_format': self.geo_format_var.get()
            }
        
        # Hiển thị frame tương ứng với mode được chọn
        selected_mode = self.mode_var.get()
        
        # Đồng bộ tab chính với mode được chọn
        if hasattr(self, 'main_notebook'):
            if selected_mode == "presentation":
                self.main_notebook.select(0)  # Chọn tab presentation
            else:
                self.main_notebook.select(1)  # Chọn tab research
        
        if selected_mode == "presentation":
            # Áp dụng các cài đặt cho chế độ presentation
            self.output_format_var.set(self.presentation_settings['output_format'])
            self.remove_white_bg.set(self.presentation_settings['remove_white_bg'])
            self.remove_black_bg.set(self.presentation_settings['remove_black_bg'])
            self.brightness_var.set(self.presentation_settings['brightness'])
            self.contrast_var.set(self.presentation_settings['contrast'])
            self.saturation_var.set(self.presentation_settings['saturation'])
            self.scale_ratio_var.set(self.presentation_settings['scale_ratio'])
        else:  # research
            # Áp dụng các cài đặt cho chế độ research
            self.output_format_var.set(self.research_settings['output_format'])
            self.remove_white_bg.set(self.research_settings['remove_white_bg'])
            self.remove_black_bg.set(self.research_settings['remove_black_bg'])
            self.brightness_var.set(self.research_settings['brightness'])
            self.contrast_var.set(self.research_settings['contrast'])
            self.saturation_var.set(self.research_settings['saturation'])
            self.scale_ratio_var.set(self.research_settings['scale_ratio'])
            
            # Trong chế độ nghiên cứu, luôn bật lưu thông tin địa lý
            self.preserve_geospatial.set(True)
            self.geo_format_var.set(self.research_settings.get('geo_format', 'GeoTIFF (.tif)'))
            
            # Ở chế độ nghiên cứu, luôn bật chức năng địa lý
            self.enable_reproject.set(True)
            
        # Cập nhật trạng thái tùy chọn hệ tọa độ sau khi đổi mode
        self._update_geo_options()
        
        # Log thông tin chuyển đổi chế độ
        self.logger.log(f"{ICONS['options']} {self._('switched_to_mode')}: {self._(selected_mode + '_mode')}")
        
    def _update_theme(self, *args):
        """Cập nhật chủ đề khi người dùng thay đổi"""
        theme = self.theme_var.get()
        self.style = ttk.Style(theme)
        
        # Kiểm tra xem đây có phải là chủ đề tối không
        is_dark = theme in ["darkly", "superhero", "solar"]
        self.is_dark_mode.set(is_dark)
        
        # Cập nhật màu log text nếu tab log đã được khởi tạo
        if hasattr(self, 'log_text'):
            bg_color = "#f7f7f7" if not is_dark else "#2a2a2a"
            fg_color = "#000000" if not is_dark else "#ffffff"
            self.log_text.config(bg=bg_color, fg=fg_color)
            
        # Lưu cấu hình
        self._save_config()
        
    def _update_language(self, *args):
        """Cập nhật ngôn ngữ khi người dùng thay đổi"""
        if not self.ui_initialized:
            return
            
        # Cập nhật tiêu đề cửa sổ
        self.master.title(self._("app_title"))
        
        # Cập nhật tiêu đề cho các tab chính
        if hasattr(self, 'main_notebook'):
            self.main_notebook.tab(0, text=f"{ICONS['presentation']} {self._('presentation_mode')}")
            self.main_notebook.tab(1, text=f"{ICONS['research']} {self._('research_mode')}")
            
        # Cập nhật tên các tab trong mode presentation
        if hasattr(self, 'presentation_notebook'):
            presentation_tabs = {
                0: self._("input_output_tab"),
                1: self._("image_adjustment_tab")
            }
            
            for idx, text in presentation_tabs.items():
                if idx < self.presentation_notebook.index('end'):
                    icon_key = "input" if idx == 0 else "adjust"
                    self.presentation_notebook.tab(idx, text=f"{ICONS.get(icon_key, '📄')} {text}")
                    
        # Cập nhật tên các tab trong mode research
        if hasattr(self, 'research_notebook'):
            research_tabs = {
                0: self._("input_output_tab"),
                1: self._("geo_tab"),
                2: self._("metadata_tab")
            }
            
            for idx, text in research_tabs.items():
                if idx < self.research_notebook.index('end'):
                    icon_key = "input" if idx == 0 else "geo" if idx == 1 else "options"
                    self.research_notebook.tab(idx, text=f"{ICONS.get(icon_key, '📄')} {text}")
                    
        # Cập nhật các thành phần giao diện khác
        if hasattr(self, 'start_button'):
            self.start_button.config(text=f"{ICONS['convert']} {self._('start_processing')}")
            
        # Cập nhật nút cài đặt
        if hasattr(self, 'settings_button'):
            self.settings_button.config(text=f"{ICONS['settings']} {self._('settings_button')}")
            
        # Cập nhật nút trợ giúp
        if hasattr(self, 'help_button'):
            self.help_button.config(text=f"{ICONS['help']} {self._('help_button')}")
        
        # Cập nhật tiêu đề khung log
        if hasattr(self, 'log_frame'):
            self.log_frame.config(text=f"{ICONS['info']} {self._('log_tab')}")
            
        # Cập nhật tiêu đề khung tiến trình
        if hasattr(self, 'progress_frame'):
            self.progress_frame.config(text=f"{ICONS['progress']} {self._('progress')}")
            
        # Cập nhật nội dung các tab - gọi phương thức update_language nếu có
        if hasattr(self, 'basic_tab') and hasattr(self.basic_tab, 'update_language'):
            self.basic_tab.update_language()
            
        if hasattr(self, 'research_basic_tab') and hasattr(self.research_basic_tab, 'update_language'):
            self.research_basic_tab.update_language()
            
        if hasattr(self, 'geo_tab') and hasattr(self.geo_tab, 'update_language'):
            self.geo_tab.update_language()
            
        if hasattr(self, 'adjust_tab') and hasattr(self.adjust_tab, 'update_language'):
            self.adjust_tab.update_language()
            
        if hasattr(self, 'research_options_tab') and hasattr(self.research_options_tab, 'update_language'):
            self.research_options_tab.update_language()
            
        # Cập nhật trạng thái hiện tại
        if self.is_processing:
            self.status_var.set(self._("processing"))
        else:
            self.status_var.set(self._("ready"))
                    
        # Lưu cấu hình
        self._save_config()
        
    def _update_geo_options(self):
        """Cập nhật trạng thái các tùy chọn xuất ảnh địa lý"""
        # Kiểm tra xem UI đã được khởi tạo chưa
        if not hasattr(self, 'ui_initialized') or not self.ui_initialized:
            return
            
        if not hasattr(self, 'geo_tab') or not hasattr(self.geo_tab, 'geo_format_menu'):
            return
            
        # Kiểm tra chế độ xử lý
        is_research_mode = self.mode_var.get() == "research"
        
        # Luôn bật các tùy chọn hệ tọa độ khi ở chế độ nghiên cứu
        if is_research_mode:
            self.enable_reproject.set(True)
            self.preserve_geospatial.set(True)  # Luôn bật lưu thông tin địa lý
            
            # Kích hoạt menu chọn định dạng
            if hasattr(self.geo_tab, 'geo_format_menu'):
                self.geo_tab.geo_format_menu["state"] = "normal"
                
            # Tự động đổi định dạng xuất thành .tif
            if self.output_format_var.get() != ".tif":
                self.output_format_var.set(".tif")
        else:
            # Khi ở chế độ báo cáo, giữ nguyên cách hoạt động
            if self.enable_reproject.get():
                self.preserve_geospatial.set(True)  # Luôn bật lưu thông tin địa lý
                self.geo_tab.geo_format_menu["state"] = "normal"
                # Tự động đổi định dạng xuất thành .tif khi bật lưu thông tin địa lý
                if self.output_format_var.get() != ".tif":
                    self.output_format_var.set(".tif")
            else:
                self.preserve_geospatial.set(False)
                self.geo_tab.geo_format_menu["state"] = "disabled"
            
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
        
        # Cài đặt chế độ xử lý
        self.mode_var.set(get_config("processing_mode", "presentation"))
        
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
        # Lưu cài đặt chung
        config = {
            # Thông tin cơ bản
            "last_input": self.input_folder,
            "last_output": self.output_folder,
            
            # Cài đặt chế độ xử lý
            "processing_mode": self.mode_var.get(),
            
            # Cài đặt hệ tọa độ chung
            "target_crs": self.target_crs_var.get(),
            
            # Cài đặt giao diện
            "theme": self.theme_var.get(),
            "language": self.language_var.get(),
            
            # Cài đặt cho mode presentation
            "presentation_output_format": self.presentation_settings['output_format'],
            "presentation_remove_white_bg": self.presentation_settings['remove_white_bg'],
            "presentation_remove_black_bg": self.presentation_settings['remove_black_bg'],
            "presentation_brightness": self.presentation_settings['brightness'],
            "presentation_contrast": self.presentation_settings['contrast'],
            "presentation_saturation": self.presentation_settings['saturation'],
            "presentation_scale_ratio": self.presentation_settings['scale_ratio'],
            
            # Cài đặt cho mode research
            "research_output_format": self.research_settings['output_format'],
            "research_remove_white_bg": self.research_settings['remove_white_bg'],
            "research_remove_black_bg": self.research_settings['remove_black_bg'],
            "research_brightness": self.research_settings['brightness'],
            "research_contrast": self.research_settings['contrast'],
            "research_saturation": self.research_settings['saturation'],
            "research_scale_ratio": self.research_settings['scale_ratio'],
            "research_preserve_geospatial": self.research_settings['preserve_geospatial'],
            "research_geo_format": self.research_settings['geo_format']
        }
        
        # Cập nhật các cài đặt của mode hiện tại
        current_mode = self.mode_var.get()
        if current_mode == "presentation":
            self.presentation_settings['output_format'] = self.output_format_var.get()
            self.presentation_settings['remove_white_bg'] = self.remove_white_bg.get()
            self.presentation_settings['remove_black_bg'] = self.remove_black_bg.get()
            self.presentation_settings['brightness'] = self.brightness_var.get()
            self.presentation_settings['contrast'] = self.contrast_var.get()
            self.presentation_settings['saturation'] = self.saturation_var.get()
            self.presentation_settings['scale_ratio'] = self.scale_ratio_var.get()
        else:
            self.research_settings['output_format'] = self.output_format_var.get()
            self.research_settings['remove_white_bg'] = self.remove_white_bg.get()
            self.research_settings['remove_black_bg'] = self.remove_black_bg.get()
            self.research_settings['brightness'] = self.brightness_var.get()
            self.research_settings['contrast'] = self.contrast_var.get()
            self.research_settings['saturation'] = self.saturation_var.get()
            self.research_settings['scale_ratio'] = self.scale_ratio_var.get()
            self.research_settings['preserve_geospatial'] = self.preserve_geospatial.get()
            self.research_settings['geo_format'] = self.geo_format_var.get()
        
        # Đồng bộ lại dictionary
        config.update({
            "presentation_output_format": self.presentation_settings['output_format'],
            "presentation_remove_white_bg": self.presentation_settings['remove_white_bg'],
            "presentation_remove_black_bg": self.presentation_settings['remove_black_bg'],
            "presentation_brightness": self.presentation_settings['brightness'],
            "presentation_contrast": self.presentation_settings['contrast'],
            "presentation_saturation": self.presentation_settings['saturation'],
            "presentation_scale_ratio": self.presentation_settings['scale_ratio'],
            
            "research_output_format": self.research_settings['output_format'],
            "research_remove_white_bg": self.research_settings['remove_white_bg'],
            "research_remove_black_bg": self.research_settings['remove_black_bg'],
            "research_brightness": self.research_settings['brightness'],
            "research_contrast": self.research_settings['contrast'],
            "research_saturation": self.research_settings['saturation'],
            "research_scale_ratio": self.research_settings['scale_ratio'],
            "research_preserve_geospatial": self.research_settings['preserve_geospatial'],
            "research_geo_format": self.research_settings['geo_format']
        })
        
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
            
            # Bật các tùy chọn địa lý
            self.enable_reproject.set(True)
            self.preserve_geospatial.set(True)
            
            # Nếu đang ở chế độ nghiên cứu, cập nhật định dạng xuất
            if self.mode_var.get() == "research":
                self.output_format_var.set(".tif")
            
            # Cập nhật giao diện
            self._update_geo_options()
            
            self.logger.log(f"✅ {self._('geo_enabled')}")
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
        
        # Xác định chế độ xử lý dựa trên tab đang được chọn
        current_tab = self.main_notebook.index('current') if hasattr(self, 'main_notebook') else 0
        processing_mode = "research" if current_tab == 1 else "presentation"
        self.mode_var.set(processing_mode)  # Cập nhật biến mode_var
        
        self.logger.log(f"{ICONS['info']} {self._('selected_mode')}: {self._(processing_mode + '_group')}")
        
        # Sử dụng luồng riêng để không treo giao diện
        thread = threading.Thread(target=lambda: self._process_images(processing_mode), daemon=True)
        thread.start()
        
    def _process_images(self, processing_mode):
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
        
        # Xử lý ảnh theo chế độ khác nhau
        processed_files = []
        
        if processing_mode == "presentation":
            # Chế độ xử lý cho báo cáo, slide - KHÔNG sử dụng thông tin địa lý
            self.logger.log(f"🖼️ Đang xử lý ở chế độ báo cáo/trình chiếu")
            
            # Sử dụng cài đặt dành riêng cho chế độ trình chiếu
            img_options = {
                'output_format': self.output_format_var.get(),
                'scale_ratio': self.scale_ratio_var.get(),
                'remove_black': self.remove_black_bg.get(),
                'remove_white': self.remove_white_bg.get(),
                'brightness': self.brightness_var.get(),
                'contrast': self.contrast_var.get(),
                'saturation': self.saturation_var.get()
            }
            
            # Xử lý từng ảnh
            for idx, path in enumerate(files, 1):
                # Cập nhật thanh tiến trình
                self.progress["value"] = idx
                self.master.update_idletasks()
                
                try:
                    # Xử lý ảnh thông thường - không bảo tồn thông tin địa lý
                    self.logger.log(f"🔄 Xử lý ảnh thông thường: {os.path.basename(path)}")
                    output_path = self.image_processor.process_image(path, self.output_folder, **img_options)
                    
                    if output_path:
                        self.logger.log(f"✅ Đã lưu ảnh tại: {output_path}")
                        processed_files.append(output_path)
                    
                    # Cập nhật giao diện và log
                    pct = (idx / total) * 100
                    self.logger.log(f"✅ [{idx}/{total}] {self._('completed')} ({pct:.2f}%)")
                    
                except Exception as e:
                    self.logger.log(f"❌ {self._('error_prefix')} {os.path.basename(path)}: {e}")
                    
        elif processing_mode == "research":
            # Chế độ xử lý cho nghiên cứu, tính toán - tập trung vào dữ liệu địa lý
            self.logger.log(f"🌎 Đang xử lý ở chế độ nghiên cứu với thông tin địa lý")
            
            # Bước 1: Chuẩn bị dữ liệu đầu vào
            self.logger.log(f"⚙️ Bước 1: Chuẩn bị dữ liệu đầu vào")
            
            # Lọc các file TIF để xử lý
            tif_files = [f for f in files if f.lower().endswith(('.tif', '.tiff'))]
            if not tif_files:
                self.logger.log(f"⚠️ Không tìm thấy file TIFF nào trong số {len(files)} file được chọn")
                self.logger.log(f"❌ Quá trình chuyển đổi hệ tọa độ không thể thực hiện")
                self.status_var.set(self._("no_tiff_found"))
                self.is_processing = False
                return
            
            self.logger.log(f"✅ Đã tìm thấy {len(tif_files)} file TIFF để xử lý")
            
            # Xác định hệ tọa độ đích
            dst_crs = ""
            for name, code in COMMON_CRS.items():
                if name == self.target_crs_var.get():
                    dst_crs = code
                    break
            
            if not dst_crs:
                self.logger.log(f"⚠️ Không thể xác định hệ tọa độ đích, sử dụng EPSG:4326 mặc định")
                dst_crs = "EPSG:4326"
            
            self.logger.log(f"🎯 Hệ tọa độ đích: {dst_crs}")
            
            # Chọn định dạng đầu ra
            geo_ext = ".tif"
            output_driver = "GTiff"
            
            if self.geo_format_var.get() != "GeoTIFF (.tif)":
                if self.geo_format_var.get() == "GeoJPEG2000 (.jp2)":
                    geo_ext = ".jp2"
                    output_driver = "JP2OpenJPEG"
                elif self.geo_format_var.get() == "ERDAS Imagine (.img)":
                    geo_ext = ".img"
                    output_driver = "HFA"
                elif self.geo_format_var.get() == "NetCDF (.nc)":
                    geo_ext = ".nc"
                    output_driver = "netCDF"
                elif self.geo_format_var.get() == "ESRI Grid (.grd)":
                    geo_ext = ".grd"
                    output_driver = "AIG"
                elif self.geo_format_var.get() == "MBTiles (.mbtiles)":
                    geo_ext = ".mbtiles"
                    output_driver = "MBTiles"
                elif self.geo_format_var.get() == "GeoPackage (.gpkg)":
                    geo_ext = ".gpkg"
                    output_driver = "GPKG"
                elif self.geo_format_var.get() == "ESRI Shapefile (.shp)":
                    geo_ext = ".shp"
                    output_driver = "ESRI Shapefile"
                    
                self.logger.log(f"📄 Định dạng xuất: {self.geo_format_var.get()}")
            
            # Xử lý từng file
            for idx, path in enumerate(tif_files, 1):
                self.progress["value"] = idx
                self.master.update_idletasks()
                
                try:
                    # Tạo đường dẫn đầu ra
                    base_name = os.path.splitext(os.path.basename(path))[0]
                    output_path = os.path.join(self.output_folder, f"{base_name}{geo_ext}")
                    
                    # Bước 2: Đọc thông tin ảnh gốc
                    self.logger.log(f"⚙️ Bước 2: Đọc thông tin ảnh gốc - {os.path.basename(path)}")
                    
                    try:
                        with rasterio.open(path) as src:
                            # Kiểm tra xem ảnh có thông tin hệ tọa độ không
                            if not src.crs:
                                self.logger.log(f"⚠️ File {os.path.basename(path)} không có thông tin hệ tọa độ")
                                self.logger.log(f"❌ Không thể chuyển đổi hệ tọa độ cho file này")
                                continue
                                
                            # Hiển thị thông tin về ảnh gốc
                            source_crs = src.crs
                            self.logger.log(f"ℹ️ Hệ tọa độ gốc: {source_crs}")
                            self.logger.log(f"ℹ️ Kích thước: {src.width}x{src.height} pixels")
                            self.logger.log(f"ℹ️ Số band: {src.count}")
                            self.logger.log(f"ℹ️ Độ phân giải: {src.res}")
                            
                            # Kiểm tra xem có cần chuyển đổi không
                            if str(source_crs) == str(dst_crs) and os.path.splitext(path)[1].lower() == geo_ext.lower():
                                self.logger.log(f"ℹ️ Hệ tọa độ nguồn và đích giống nhau, sao chép file")
                                import shutil
                                shutil.copy2(path, output_path)
                                self.logger.log(f"✅ Đã sao chép ảnh tại: {output_path}")
                                processed_files.append(output_path)
                                continue
                            
                            # Bước 3: Tính toán thông tin ảnh sau khi chuyển hệ tọa độ
                            self.logger.log(f"⚙️ Bước 3: Tính toán thông tin ảnh sau khi chuyển hệ tọa độ")
                            
                            from rasterio.warp import calculate_default_transform, Resampling
                            
                            # Tính toán transformation mới
                            transform, width, height = calculate_default_transform(
                                source_crs, dst_crs, src.width, src.height, *src.bounds)
                            
                            self.logger.log(f"ℹ️ Kích thước mới: {width}x{height} pixels")
                            
                            # Chuẩn bị metadata cho ảnh đầu ra
                            out_kwargs = src.meta.copy()
                            out_kwargs.update({
                                'crs': dst_crs,
                                'transform': transform,
                                'width': width,
                                'height': height,
                                'driver': output_driver
                            })
                            
                            # Bước 4: Thực hiện chuyển đổi hệ tọa độ
                            self.logger.log(f"⚙️ Bước 4: Thực hiện chuyển đổi hệ tọa độ")
                            
                            from rasterio.warp import reproject
                            
                            # Đảm bảo thư mục đầu ra tồn tại
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                            
                            # Thực hiện reprojection
                            with rasterio.open(output_path, 'w', **out_kwargs) as dst:
                                for i in range(1, src.count + 1):
                                    self.logger.log(f"🔄 Đang xử lý band {i}/{src.count}")
                                    
                                    # Đọc dữ liệu từ band gốc
                                    source = src.read(i)
                                    
                                    # Chuẩn bị mảng đích
                                    destination = np.zeros((height, width), dtype=source.dtype)
                                    
                                    # Thực hiện reprojection
                                    reproject(
                                        source,
                                        destination,
                                        src_transform=src.transform,
                                        src_crs=source_crs,
                                        dst_transform=transform,
                                        dst_crs=dst_crs,
                                        resampling=Resampling.nearest
                                    )
                                    
                                    # Ghi dữ liệu vào band trong file đầu ra
                                    dst.write(destination, i)
                            
                            # Bước 5: Ghi ảnh TIFF mới
                            self.logger.log(f"⚙️ Bước 5: Hoàn tất ghi ảnh {geo_ext} mới")
                            self.logger.log(f"✅ Đã lưu file tại: {output_path}")
                            processed_files.append(output_path)
                
                            # Bước 6: Thông báo kết quả
                            self.logger.log(f"⚙️ Bước 6: Kết quả chuyển đổi hệ tọa độ")
                            self.logger.log(f"✅ Chuyển đổi thành công từ {source_crs} sang {dst_crs}")
                            self.logger.log(f"ℹ️ Tổng quan: {src.width}x{src.height} → {width}x{height} pixels")
                    
                    except rasterio.errors.RasterioIOError as e:
                        self.logger.log(f"❌ Lỗi khi mở file {os.path.basename(path)}: {str(e)}")
                    except Exception as e:
                        self.logger.log(f"❌ Lỗi khi xử lý {os.path.basename(path)}: {str(e)}")
                    
                    # Cập nhật tiến trình
                    pct = (idx / len(tif_files)) * 100
                    self.logger.log(f"✅ [{idx}/{len(tif_files)}] {self._('completed')} ({pct:.2f}%)")
                
                except Exception as e:
                    self.logger.log(f"❌ Lỗi không xác định khi xử lý {os.path.basename(path)}: {str(e)}")
            
            # Thông báo hoàn tất
            if processed_files:
                self.logger.log(f"🎉 Đã chuyển đổi thành công {len(processed_files)}/{len(tif_files)} file")
            else:
                self.logger.log(f"⚠️ Không có file nào được xử lý thành công")
        
        # Hoàn tất
        self.logger.log(f"🎉 {self._('all_completed')}")
        self.status_var.set(self._("completed"))
        self.is_processing = False

    def convert_coordinates(self):
        """Chuyển đổi giữa các hệ tọa độ khác nhau"""
        try:
            # Lấy giá trị tọa độ đầu vào
            x = float(self.coord_x_var.get())
            y = float(self.coord_y_var.get())
            
            # Lấy thông tin hệ tọa độ
            input_crs_name = self.input_crs_var.get()
            output_crs_name = self.output_crs_var.get()
            
            input_crs = COMMON_CRS[input_crs_name]
            output_crs = COMMON_CRS[output_crs_name]
            
            # Loại chuyển đổi
            conversion_type = self.conversion_type_var.get()
            
            # Xử lý chuyển đổi (giả lập kết quả để demo)
            # Trong thực tế sẽ gọi GeoProcessor để xử lý
            result_x = x + 10
            result_y = y + 20
            
            # Cập nhật kết quả
            self.output_coord_x_var.set(f"{result_x:.6f}")
            self.output_coord_y_var.set(f"{result_y:.6f}")
            
            # Thêm vào lịch sử
            if hasattr(self, 'coordinate_tab') and hasattr(self.coordinate_tab, 'history_text'):
                # Lấy thời gian hiện tại
                from datetime import datetime
                now = datetime.now().strftime("%H:%M:%S")
                
                # Tạo nội dung
                if conversion_type == "pixel_to_geo":
                    history_entry = f"[{now}] Pixel ({x}, {y}) → {output_crs_name}: ({result_x:.6f}, {result_y:.6f})\n"
                else:
                    history_entry = f"[{now}] {input_crs_name} ({x}, {y}) → Pixel: ({result_x:.6f}, {result_y:.6f})\n"
                
                # Thêm vào lịch sử
                self.coordinate_tab.history_text.config(state="normal")
                self.coordinate_tab.history_text.insert("1.0", history_entry)
                self.coordinate_tab.history_text.config(state="disabled")
                
            # Cập nhật trạng thái
            self.status_var.set(self._("conversion_completed"))
            
        except ValueError:
            # Lỗi khi nhập không phải số
            self.logger.error(self._("invalid_coordinates"))
        except Exception as e:
            # Lỗi khác
            self.logger.error(f"{self._('conversion_error')}: {str(e)}") 

    def _setup_menu(self):
        """Thiết lập thanh menu của ứng dụng"""
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)
        
        # Menu File
        file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self._("menu_file"), menu=file_menu)
        file_menu.add_command(label=self._("select_images"), command=self.select_input)
        file_menu.add_command(label=self._("save_output"), command=self.select_output)
        file_menu.add_separator()
        file_menu.add_command(label=self._("exit"), command=self.quit)
        
        # Menu Cài đặt
        self.menu_bar.add_command(
            label=self._("settings_button"),
            command=self._open_settings_dialog
        )
        
        # Menu Trợ giúp
        help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self._("menu_help"), menu=help_menu)
        help_menu.add_command(label=self._("about"), command=self._show_about)

    def _open_settings_dialog(self):
        """Mở cửa sổ cài đặt"""
        from ui.dialogs.settings_dialog import SettingsDialog
        settings = SettingsDialog(self.master, self)
        # Không cần gọi grab_set vì đã được thiết lập trong SettingsDialog

    def _show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        from ui.dialogs.about_dialog import AboutDialog
        from PyQt5.QtWidgets import QApplication
        import sys
        
        # Create QApplication instance if it doesn't exist
        if not QApplication.instance():
            qt_app = QApplication(sys.argv)
            
        about = AboutDialog(None)  # Use None instead of self as parent
        about.exec_()  # Use exec_ instead of grab_set for Qt dialogs

    def _init_mode_settings(self):
        """Cập nhật cài đặt mặc định cho từng mode từ config file"""
        # Cài đặt cho chế độ presentation
        self.presentation_settings['output_format'] = get_config("presentation_output_format", ".png")
        self.presentation_settings['remove_white_bg'] = get_config("presentation_remove_white_bg", False)
        self.presentation_settings['remove_black_bg'] = get_config("presentation_remove_black_bg", False)
        self.presentation_settings['brightness'] = get_config("presentation_brightness", "1.0")
        self.presentation_settings['contrast'] = get_config("presentation_contrast", "1.0")
        self.presentation_settings['saturation'] = get_config("presentation_saturation", "1.0")
        self.presentation_settings['scale_ratio'] = get_config("presentation_scale_ratio", "1.0")
        
        # Cài đặt cho chế độ research
        self.research_settings['output_format'] = get_config("research_output_format", ".tif")
        self.research_settings['remove_white_bg'] = get_config("research_remove_white_bg", False)
        self.research_settings['remove_black_bg'] = get_config("research_remove_black_bg", False)
        self.research_settings['brightness'] = get_config("research_brightness", "1.0")
        self.research_settings['contrast'] = get_config("research_contrast", "1.0")
        self.research_settings['saturation'] = get_config("research_saturation", "1.0")
        self.research_settings['scale_ratio'] = get_config("research_scale_ratio", "1.0")
        self.research_settings['preserve_geospatial'] = get_config("research_preserve_geospatial", True)
        self.research_settings['geo_format'] = get_config("research_geo_format", "GeoTIFF (.tif)")

# Tạo lớp ResearchBasicTab kế thừa từ BasicTab nhưng không hiển thị định dạng xuất
class ResearchBasicTab(BasicTab):
    """Tab cơ bản cho chế độ nghiên cứu, không hiển thị định dạng xuất"""
    
    def update_language(self):
        """Cập nhật ngôn ngữ cho tất cả các thành phần"""
        # Gọi phương thức update_language của lớp cha
        BasicTab.update_language(self)
        
        # Lưu lại tham chiếu đến các widget để cập nhật
        if hasattr(self, 'input_frame'):
            self.input_frame.config(text=f"{ICONS['input']} {self.app._('input_title')}")
            
        if hasattr(self, 'output_frame'):
            self.output_frame.config(text=f"{ICONS['output']} {self.app._('output_title')}")
            
        if hasattr(self, 'select_folder_btn'):
            self.select_folder_btn.config(text=self.app._("select_folder"))
            
        if hasattr(self, 'select_files_btn'):
            self.select_files_btn.config(text=self.app._("select_files"))
            
        if hasattr(self, 'drag_drop_tip'):
            self.drag_drop_tip.config(text=f"💡 {self.app._('drag_drop_tip')}")
            
        if hasattr(self, 'output_select_btn'):
            self.output_select_btn.config(text=self.app._("select_folder"))
    
    def build(self):
        """Xây dựng giao diện tab loại bỏ phần định dạng xuất"""
        # Phần nhập liệu
        self.input_frame = ttk.LabelFrame(
            self.parent, 
            text=f"{ICONS['input']} {self.app._('input_title')}", 
            padding=10,
            bootstyle="primary"
        )
        self.input_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        input_group = ttk.Frame(self.input_frame)
        input_group.pack(fill="x")
        
        self.input_entry = ttk.Entry(
            input_group, 
            textvariable=self.app.input_path_var, 
            state="readonly", 
            font=self.app.normal_font
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=4)
        
        button_frame = ttk.Frame(input_group)
        button_frame.pack(side="right", padx=(5, 0))
        
        self.select_folder_btn = ttk.Button(
            button_frame, 
            text=self.app._("select_folder"), 
            command=self.app.browse_input_folder,
            bootstyle="outline"
        )
        self.select_folder_btn.pack(side="left", padx=(0, 5))
        
        self.select_files_btn = ttk.Button(
            button_frame, 
            text=self.app._("select_files"), 
            command=self.app.browse_input,
            bootstyle="outline"
        )
        self.select_files_btn.pack(side="left")
        
        # Hỗ trợ kéo thả
        self.input_entry.drop_target_register(DND_FILES)
        self.input_entry.dnd_bind('<<Drop>>', self.app.handle_drop_input)
        
        tip_frame = ttk.Frame(self.input_frame)
        tip_frame.pack(fill="x", pady=(5, 0))
        self.drag_drop_tip = ttk.Label(
            tip_frame, 
            text=f"💡 {self.app._('drag_drop_tip')}", 
            font=self.app.small_font,
            foreground="gray"
        )
        self.drag_drop_tip.pack(side="left")
        
        # Phần xuất
        self.output_frame = ttk.LabelFrame(
            self.parent, 
            text=f"{ICONS['output']} {self.app._('output_title')}", 
            padding=10,
            bootstyle="primary"
        )
        self.output_frame.pack(fill="x", ipady=5)
        
        output_group = ttk.Frame(self.output_frame)
        output_group.pack(fill="x")
        
        self.output_entry = ttk.Entry(
            output_group, 
            textvariable=self.app.output_path_var, 
            state="readonly",
            font=self.app.normal_font
        )
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=4)
        
        self.output_select_btn = ttk.Button(
            output_group, 
            text=self.app._("select_folder"), 
            command=self.app.browse_output,
            bootstyle="outline"
        )
        self.output_select_btn.pack(side="right", padx=(5, 0))
        
        # Hỗ trợ kéo thả
        self.output_entry.drop_target_register(DND_FILES)
        self.output_entry.dnd_bind('<<Drop>>', self.app.handle_drop_output)

    def _format_changed(self, *args):
        """Xử lý khi người dùng thay đổi định dạng ảnh"""
        pass  # Không còn cần thiết trong tab nghiên cứu 

# Tạo lớp ResearchOptionsTab kế thừa từ OptionsTab nhưng không hiển thị phần cài đặt
class ResearchOptionsTab(OptionsTab):
    """Tab tùy chọn cho chế độ nghiên cứu, chỉ hiển thị phần xuất metadata"""
    
    def update_language(self):
        """Cập nhật ngôn ngữ cho tất cả các thành phần"""
        # Gọi phương thức update_language của lớp cha
        OptionsTab.update_language(self)
        
        if hasattr(self, 'metadata_frame'):
            self.metadata_frame.config(text=self.app._("metadata_export"))
            
        if hasattr(self, 'export_csv_btn'):
            self.export_csv_btn.config(text=self.app._("export_csv"))
            
        if hasattr(self, 'export_json_btn'):
            self.export_json_btn.config(text=self.app._("export_json"))
    
    def build(self):
        """Xây dựng giao diện tab chỉ hiển thị phần xuất metadata"""
        # Thêm tùy chọn xuất metadata
        self.metadata_frame = ttk.LabelFrame(self.parent, text=self.app._("metadata_export"), padding=10)
        self.metadata_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        button_frame = ttk.Frame(self.metadata_frame)
        button_frame.pack(fill="x", pady=(5, 0))
        
        self.export_csv_btn = ttk.Button(
            button_frame,
            text=self.app._("export_csv"),
            command=lambda: self.app.export_metadata("csv"),
            bootstyle="info-outline",
            width=15
        )
        self.export_csv_btn.pack(side="left", padx=(0, 5))
        
        self.export_json_btn = ttk.Button(
            button_frame,
            text=self.app._("export_json"),
            command=lambda: self.app.export_metadata("json"),
            bootstyle="info-outline",
            width=15
        )
        self.export_json_btn.pack(side="left")
        
        # Phần thông tin về phiên bản
        version_frame = ttk.Frame(self.parent)
        version_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        ttk.Label(
            version_frame,
            text="TifTiff v1.1 - © 2025",
            font=("Segoe UI", 8),
            foreground="#888888"
        ).pack(side="right") 