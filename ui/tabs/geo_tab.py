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
        
    def update_language(self):
        """Cập nhật ngôn ngữ cho tất cả các thành phần"""
        if hasattr(self, 'src_frame'):
            self.src_frame.config(text=f"{ICONS['source_crs']} {self.app._('source_crs')}")
            
        if hasattr(self, 'detected_label'):
            self.detected_label.config(text=f"{ICONS['detected_crs']} {self.app._('detected_crs')}")
            
        if hasattr(self, 'check_crs_btn'):
            self.check_crs_btn.config(text=self.app._('check_crs'))
            
        if hasattr(self, 'target_frame'):
            self.target_frame.config(text=f"{ICONS['target_crs']} {self.app._('target_crs')}")
            
        if hasattr(self, 'export_frame'):
            self.export_frame.config(text=f"{ICONS['geo_export']} {self.app._('geo_export')}")
            
        if hasattr(self, 'geo_format_label'):
            self.geo_format_label.config(text=self.app._('geo_format'))
            
        if hasattr(self, 'geo_guide_label'):
            self.geo_guide_label.config(text=f"{ICONS['geo_guide']} {self.app._('geo_guide')}")
    
    def build(self):
        """Xây dựng giao diện tab"""
        # Tạo phân chia không gian: phần trên cho cài đặt, phần dưới cho thông tin
        top_frame = ttk.Frame(self.parent)
        top_frame.pack(fill="both", expand=False)
        
        bottom_frame = ttk.Frame(self.parent)
        bottom_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Khung chính cho phần cài đặt
        main_frame = ttk.Frame(top_frame)
        main_frame.pack(fill="both", expand=True)
        
        # Panel trái - Chọn hệ tọa độ
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Chọn hệ tọa độ nguồn
        self.src_frame = ttk.LabelFrame(left_panel, text=f"{ICONS['source_crs']} {self.app._('source_crs')}", padding=10)
        self.src_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        src_crs_options = ["Tự động phát hiện"] + list(COMMON_CRS.keys())
        ttk.OptionMenu(
            self.src_frame, 
            self.app.source_crs_var, 
            self.app.source_crs_var.get(), 
            *src_crs_options,
            bootstyle="primary"
        ).pack(fill="x", pady=(0, 10))
        
        # Thêm phần hiển thị hệ tọa độ đã phát hiện
        detect_frame = ttk.Frame(self.src_frame)
        detect_frame.pack(fill="x")
        self.detected_label = ttk.Label(detect_frame, text=f"{ICONS['detected_crs']} {self.app._('detected_crs')}")
        self.detected_label.pack(side="left")
        
        # Label hiển thị hệ tọa độ được phát hiện
        ttk.Label(
            detect_frame,
            textvariable=self.app.detected_crs_var,
            font=("Segoe UI", 9, "italic"),
            foreground="blue"
        ).pack(side="left", padx=5)
        
        # Nút kiểm tra hệ tọa độ
        self.check_crs_btn = ttk.Button(
            self.src_frame,
            text=self.app._('check_crs'),
            command=self.app.detect_crs,
            bootstyle="info-outline"
        )
        self.check_crs_btn.pack(fill="x", pady=(10, 0))
        
        # Chọn hệ tọa độ đích
        self.target_frame = ttk.LabelFrame(left_panel, text=f"{ICONS['target_crs']} {self.app._('target_crs')}", padding=10)
        self.target_frame.pack(fill="x", ipady=5)
        
        # Tạo dropdown menu chọn hệ tọa độ đích
        ttk.OptionMenu(
            self.target_frame, 
            self.app.target_crs_var, 
            self.app.target_crs_var.get(), 
            *COMMON_CRS.keys(),
            bootstyle="primary"
        ).pack(fill="x")
        
        # Panel phải - Tùy chọn xuất ảnh
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Xuất ảnh với hệ tọa độ
        self.export_frame = ttk.LabelFrame(right_panel, text=f"{ICONS['geo_export']} {self.app._('geo_export')}", padding=10)
        self.export_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        # Phần giữ lại: Định dạng ảnh khi xuất với thông tin hệ tọa độ
        format_frame = ttk.Frame(self.export_frame)
        format_frame.pack(fill="x")
        
        self.geo_format_label = ttk.Label(format_frame, text=self.app._('geo_format'))
        self.geo_format_label.pack(side="left")
        
        # Tạo menu và lưu tham chiếu trực tiếp trong tab này
        self.geo_format_menu = ttk.OptionMenu(
            format_frame,
            self.app.geo_format_var,
            self.app.geo_format_var.get(),
            "GeoTIFF (.tif)",
            "GeoJPEG2000 (.jp2)",
            "GeoPackage (.gpkg)",
            "ESRI Shapefile (.shp)"
        )
        self.geo_format_menu.pack(side="left", padx=(5, 0), fill="x", expand=True)
        
        # Lưu trữ tham chiếu trong app
        self.app.geo_format_menu = self.geo_format_menu
        
        # Thêm hướng dẫn
        info_frame = ttk.Frame(top_frame)
        info_frame.pack(fill="x", pady=(15, 0))
        
        self.geo_guide_label = ttk.Label(
            info_frame, 
            text=f"{ICONS['geo_guide']} {self.app._('geo_guide')}",
            font=self.app.small_font,
            foreground="#555555"
        )
        self.geo_guide_label.pack(anchor="w")
        
        # Thêm thông tin mô tả các định dạng trong phần bottom_frame
        format_info_frame = ttk.LabelFrame(bottom_frame, text="Thông tin định dạng hỗ trợ", padding=10)
        format_info_frame.pack(fill="both", expand=True)
        
        format_info_text = ttk.Text(
            format_info_frame,
            height=12,
            width=50,
            font=self.app.small_font,
            wrap="word"
        )
        format_info_text.pack(fill="both", expand=True)
        
        # Nội dung mô tả
        format_info = """
• GeoTIFF (.tif) - Định dạng chuẩn, hỗ trợ tốt nhất cho dữ liệu raster địa lý. Được hỗ trợ bởi hầu hết các phần mềm GIS và xử lý ảnh.

• GeoJPEG2000 (.jp2) - Định dạng nén tốt hơn GeoTIFF, phù hợp cho ảnh lớn, giảm dung lượng lưu trữ mà vẫn duy trì chất lượng cao.

• GeoPackage (.gpkg) - Định dạng tiêu chuẩn OGC hiện đại, hỗ trợ cả dữ liệu raster và vector trong cùng một file. Thay thế tốt cho Shapefile trong nhiều ứng dụng.

• ESRI Shapefile (.shp) - Định dạng vector phổ biến, được hỗ trợ rộng rãi bởi các phần mềm GIS, mặc dù đã cũ nhưng vẫn được sử dụng rộng rãi.

Lưu ý:
- GeoTIFF (.tif) là định dạng được hỗ trợ tốt nhất và ổn định nhất cho hầu hết các ứng dụng
        """
        
        format_info_text.insert("1.0", format_info)
        format_info_text.config(state="disabled")
