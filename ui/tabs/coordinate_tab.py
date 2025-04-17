"""
Tab chuyển đổi tọa độ chi tiết cho ứng dụng TifTiff
"""

import tkinter as tk
import ttkbootstrap as ttk
from resources.constants import ICONS, COMMON_CRS

class CoordinateTab:
    """Tab chuyển đổi tọa độ chi tiết"""
    
    def __init__(self, parent, app):
        """Khởi tạo tab chuyển đổi tọa độ chi tiết"""
        self.parent = parent
        self.app = app
        self.build()
        
    def build(self):
        """Xây dựng giao diện tab"""
        # Header - Giới thiệu
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(
            header_frame,
            text=f"{ICONS['coordinate']} {self.app._('coordinate_title')}",
            font=self.app.header_font
        ).pack(anchor="w")
        
        ttk.Label(
            header_frame,
            text=self.app._('coordinate_description'),
            font=self.app.small_font,
            foreground="#555555"
        ).pack(anchor="w", pady=(5, 0))
        
        # Panel chính
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill="both", expand=True)
        
        # Panel trái - Thiết lập chuyển đổi
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Chọn kiểu chuyển đổi
        conversion_frame = ttk.LabelFrame(left_panel, text=f"{ICONS['conversion_type']} {self.app._('conversion_type')}", padding=10)
        conversion_frame.pack(fill="x", pady=(0, 15), ipady=5)
        
        self.app.conversion_type_var = tk.StringVar(value="pixel_to_geo")
        
        ttk.Radiobutton(
            conversion_frame,
            text=self.app._('pixel_to_geo'),
            variable=self.app.conversion_type_var,
            value="pixel_to_geo",
            bootstyle="primary"
        ).pack(fill="x", pady=(0, 5))
        
        ttk.Radiobutton(
            conversion_frame,
            text=self.app._('geo_to_pixel'),
            variable=self.app.conversion_type_var,
            value="geo_to_pixel",
            bootstyle="primary"
        ).pack(fill="x")
        
        # Tọa độ đầu vào
        input_frame = ttk.LabelFrame(left_panel, text=f"{ICONS['input_coord']} {self.app._('input_coord')}", padding=10)
        input_frame.pack(fill="x", pady=(0, 15), ipady=5)
        
        # X, Y input
        coord_frame = ttk.Frame(input_frame)
        coord_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(coord_frame, text="X:", font=self.app.normal_font).pack(side="left", padx=(0, 5))
        self.app.coord_x_var = tk.StringVar()
        ttk.Entry(coord_frame, textvariable=self.app.coord_x_var, width=15).pack(side="left", padx=(0, 15))
        
        ttk.Label(coord_frame, text="Y:", font=self.app.normal_font).pack(side="left", padx=(0, 5))
        self.app.coord_y_var = tk.StringVar()
        ttk.Entry(coord_frame, textvariable=self.app.coord_y_var, width=15).pack(side="left")
        
        # Hệ tọa độ đầu vào
        ttk.Label(input_frame, text=f"{ICONS['source_crs']} {self.app._('input_crs')}").pack(anchor="w", pady=(0, 5))
        self.app.input_crs_var = tk.StringVar(value=list(COMMON_CRS.keys())[0])
        ttk.OptionMenu(
            input_frame,
            self.app.input_crs_var,
            self.app.input_crs_var.get(),
            *COMMON_CRS.keys(),
            bootstyle="primary"
        ).pack(fill="x")
        
        # Panel phải - Kết quả
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Tọa độ đầu ra
        output_frame = ttk.LabelFrame(right_panel, text=f"{ICONS['output_coord']} {self.app._('output_coord')}", padding=10)
        output_frame.pack(fill="x", pady=(0, 15), ipady=5)
        
        # X, Y output (read-only)
        out_coord_frame = ttk.Frame(output_frame)
        out_coord_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(out_coord_frame, text="X:", font=self.app.normal_font).pack(side="left", padx=(0, 5))
        self.app.output_coord_x_var = tk.StringVar()
        ttk.Entry(
            out_coord_frame, 
            textvariable=self.app.output_coord_x_var, 
            width=15,
            state="readonly"
        ).pack(side="left", padx=(0, 15))
        
        ttk.Label(out_coord_frame, text="Y:", font=self.app.normal_font).pack(side="left", padx=(0, 5))
        self.app.output_coord_y_var = tk.StringVar()
        ttk.Entry(
            out_coord_frame, 
            textvariable=self.app.output_coord_y_var, 
            width=15,
            state="readonly"
        ).pack(side="left")
        
        # Hệ tọa độ đầu ra
        ttk.Label(output_frame, text=f"{ICONS['target_crs']} {self.app._('output_crs')}").pack(anchor="w", pady=(0, 5))
        self.app.output_crs_var = tk.StringVar(value=list(COMMON_CRS.keys())[1])
        ttk.OptionMenu(
            output_frame,
            self.app.output_crs_var,
            self.app.output_crs_var.get(),
            *COMMON_CRS.keys(),
            bootstyle="primary"
        ).pack(fill="x")
        
        # Nút chuyển đổi
        ttk.Button(
            right_panel,
            text=f"{ICONS['convert']} {self.app._('convert_coordinates')}",
            command=self.app.convert_coordinates,
            bootstyle="success",
            width=20
        ).pack(anchor="e", pady=(0, 10))
        
        # Thêm thông tin và lịch sử
        history_frame = ttk.LabelFrame(right_panel, text=f"{ICONS['history']} {self.app._('conversion_history')}", padding=10)
        history_frame.pack(fill="both", expand=True, ipady=5)
        
        # Textbox hiển thị lịch sử chuyển đổi
        self.history_text = tk.Text(
            history_frame,
            font=self.app.small_font,
            height=5,
            wrap="word",
            state="disabled"
        )
        self.history_text.pack(fill="both", expand=True)
        
        # Scrollbar cho lịch sử
        scrollbar = ttk.Scrollbar(self.history_text, command=self.history_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_text.config(yscrollcommand=scrollbar.set) 