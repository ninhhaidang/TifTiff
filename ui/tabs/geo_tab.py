"""Tab hệ tọa độ cho ứng dụng TifTiff"""

import os
import ttkbootstrap as ttk
from tkinterdnd2 import DND_FILES

from resources.constants import ICONS, COMMON_CRS

class GeoTab:
    """Tab chuyển đổi hệ tọa độ"""
    
    def __init__(self, parent, app):
        """Khởi tạo tab hệ tọa độ"""
        self.parent = parent
        self.app = app
        self.build()
        
    def build(self):
        """Xây dựng giao diện tab"""
        # Checkbox bật/tắt chức năng
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill="x", pady=(0, 10))
        
        reproject_check = ttk.Checkbutton(
            header_frame, 
            text=f"{ICONS['enable_geo']} {self.app._('enable_geo')}", 
            variable=self.app.enable_reproject,
            command=self.app._update_geo_options,
            bootstyle="success"
        )
        reproject_check.pack(side="left")
        
        # Khung chính
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True)
        
        # Panel trái - Chọn hệ tọa độ
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Chọn hệ tọa độ nguồn
        src_frame = ttk.LabelFrame(left_panel, text=f"{ICONS['source_crs']} {self.app._('source_crs')}", padding=10)
        src_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        src_crs_options = ["Tự động phát hiện"] + list(COMMON_CRS.keys())
        ttk.OptionMenu(
            src_frame, 
            self.app.source_crs_var, 
            self.app.source_crs_var.get(), 
            *src_crs_options,
            bootstyle="primary"
        ).pack(fill="x", pady=(0, 10))
        
        # Thêm phần hiển thị hệ tọa độ đã phát hiện
        detect_frame = ttk.Frame(src_frame)
        detect_frame.pack(fill="x")
        ttk.Label(detect_frame, text=f"{ICONS['detected_crs']} {self.app._('detected_crs')}").pack(side="left")
        
        # Label hiển thị hệ tọa độ được phát hiện
        ttk.Label(
            detect_frame,
            textvariable=self.app.detected_crs_var,
            font=("Segoe UI", 9, "italic"),
            foreground="blue"
        ).pack(side="left", padx=5)
        
        # Nút kiểm tra hệ tọa độ
        ttk.Button(
            src_frame,
            text=f"{ICONS['check_crs']} {self.app._('check_crs')}",
            command=self.app.detect_crs,
            bootstyle="info-outline",
            width=20
        ).pack(fill="x", pady=(10, 0))
        
        # Chọn hệ tọa độ đích
        dst_frame = ttk.LabelFrame(left_panel, text=f"{ICONS['target_crs']} {self.app._('target_crs')}", padding=10)
        dst_frame.pack(fill="x", ipady=5)
        
        ttk.OptionMenu(
            dst_frame, 
            self.app.target_crs_var, 
            self.app.target_crs_var.get(), 
            *COMMON_CRS.keys(),
            bootstyle="primary"
        ).pack(fill="x")
        
        # Panel phải - Tùy chọn xuất
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        output_frame = ttk.LabelFrame(right_panel, text=f"{ICONS['geo_export']} {self.app._('geo_export')}", padding=10)
        output_frame.pack(fill="x", ipady=5)
        
        self.app.preserve_geo_check = ttk.Checkbutton(
            output_frame,
            text=f"{ICONS['save_geo']} {self.app._('save_geo')}",
            variable=self.app.preserve_geospatial,
            state="disabled",
            bootstyle="success"
        )
        self.app.preserve_geo_check.pack(fill="x", pady=(0, 10))
        
        ttk.Label(output_frame, text=f"{ICONS['geo_format']} {self.app._('geo_format')}").pack(anchor="w")
        
        self.app.geo_format_menu = ttk.OptionMenu(
            output_frame,
            self.app.geo_format_var,
            self.app.geo_format_var.get(),
            "GeoTIFF (.tif)",
            "GeoJPEG2000 (.jp2)",
            "ERDAS Imagine (.img)",
            bootstyle="primary"
        )
        self.app.geo_format_menu.pack(fill="x", pady=(5, 0))
        self.app.geo_format_menu["state"] = "disabled"
        
        # Thêm hướng dẫn
        info_frame = ttk.Frame(self.parent)
        info_frame.pack(fill="x", pady=(15, 0))
        
        ttk.Label(
            info_frame, 
            text=f"{ICONS['geo_guide']} {self.app._('geo_guide')}",
            font=self.app.small_font,
            foreground="#555555"
        ).pack(anchor="w")
