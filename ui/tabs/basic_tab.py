"""
Tab cơ bản cho ứng dụng TifTiff
"""

import tkinter as tk
from tkinter import filedialog
import os
import ttkbootstrap as ttk
from tkinterdnd2 import DND_FILES

from resources.constants import ICONS

class BasicTab:
    """Tab cơ bản với tùy chọn nhập/xuất"""
    
    def __init__(self, parent, app):
        """Khởi tạo tab cơ bản"""
        self.parent = parent
        self.app = app
        self.build()
        
    def build(self):
        """Xây dựng giao diện tab"""
        # Phần nhập liệu
        input_frame = ttk.LabelFrame(
            self.parent, 
            text=f"{ICONS['input']} {self.app._('input_title')}", 
            padding=10,
            bootstyle="primary"
        )
        input_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        input_group = ttk.Frame(input_frame)
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
        
        ttk.Button(
            button_frame, 
            text=self.app._("select_folder"), 
            command=self.app.browse_input_folder,
            bootstyle="outline"
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text=self.app._("select_files"), 
            command=self.app.browse_input,
            bootstyle="outline"
        ).pack(side="left")
        
        # Hỗ trợ kéo thả
        self.input_entry.drop_target_register(DND_FILES)
        self.input_entry.dnd_bind('<<Drop>>', self.app.handle_drop_input)
        
        tip_frame = ttk.Frame(input_frame)
        tip_frame.pack(fill="x", pady=(5, 0))
        ttk.Label(
            tip_frame, 
            text=f"💡 {self.app._('drag_drop_tip')}", 
            font=self.app.small_font,
            foreground="gray"
        ).pack(side="left")
        
        # Phần xuất
        output_frame = ttk.LabelFrame(
            self.parent, 
            text=f"{ICONS['output']} {self.app._('output_title')}", 
            padding=10,
            bootstyle="primary"
        )
        output_frame.pack(fill="x", ipady=5)
        
        output_group = ttk.Frame(output_frame)
        output_group.pack(fill="x")
        
        self.output_entry = ttk.Entry(
            output_group, 
            textvariable=self.app.output_path_var, 
            state="readonly",
            font=self.app.normal_font
        )
        self.output_entry.pack(side="left", fill="x", expand=True, ipady=4)
        
        ttk.Button(
            output_group, 
            text=self.app._("select_folder"), 
            command=self.app.browse_output,
            bootstyle="outline"
        ).pack(side="right", padx=(5, 0))
        
        # Hỗ trợ kéo thả
        self.output_entry.drop_target_register(DND_FILES)
        self.output_entry.dnd_bind('<<Drop>>', self.app.handle_drop_output)
        
        # Định dạng xuất và scale
        format_frame = ttk.Frame(self.parent)
        format_frame.pack(fill="x", pady=(15, 0))
        
        ttk.Label(format_frame, text=self.app._("export_format"), font=self.app.normal_font).pack(side="left")
        
        ttk.OptionMenu(
            format_frame, 
            self.app.output_format_var, 
            self.app.output_format_var.get(), 
            ".png", ".jpg", ".tif", ".bmp",
            bootstyle="outline",
            command=self._format_changed
        ).pack(side="left", padx=(5, 15))
        
        ttk.Label(format_frame, text=self.app._("scale_ratio"), font=self.app.normal_font).pack(side="left")
        scale_entry = ttk.Entry(format_frame, textvariable=self.app.scale_ratio_var, width=8)
        scale_entry.pack(side="left", padx=(5, 0))
        
    def _format_changed(self, *args):
        """Xử lý khi người dùng thay đổi định dạng ảnh"""
        # Nếu định dạng ảnh chuyển đổi sang .tif, tự động bật tùy chọn lưu thông tin địa lý
        if self.app.output_format_var.get() == ".tif" and self.app.enable_reproject.get():
            self.app.preserve_geospatial.set(True)
            self.app._update_geo_options() 