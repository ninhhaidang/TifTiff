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
        
    def update_language(self):
        """Cập nhật ngôn ngữ cho tất cả các thành phần"""
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
            
        if hasattr(self, 'export_format_label'):
            self.export_format_label.config(text=self.app._("export_format"))
        
    def build(self):
        """Xây dựng giao diện tab"""
        # Phần nhập liệu
        self.input_frame = ttk.LabelFrame(
            self.parent, 
            text=f"{ICONS['input']} {self.app._('input_title')}", 
            padding=10,
            bootstyle="primary"
        )
        self.input_frame.pack(fill="x", pady=(0, 15), ipady=5)
        
        # Container cho toàn bộ phần input
        input_container = ttk.Frame(self.input_frame)
        input_container.pack(fill="x", expand=True)
        
        # Container cho entry và các nút
        input_group = ttk.Frame(input_container)
        input_group.pack(fill="x", expand=True, pady=(0, 10))
        
        self.input_entry = ttk.Entry(
            input_group, 
            textvariable=self.app.input_path_var, 
            state="readonly", 
            font=self.app.normal_font
        )
        self.input_entry.pack(side="left", fill="x", expand=True, ipady=4)
        
        button_frame = ttk.Frame(input_group)
        button_frame.pack(side="right", padx=(10, 0))
        
        self.select_folder_btn = ttk.Button(
            button_frame, 
            text=self.app._("select_folder"), 
            command=self.app.browse_input_folder,
            bootstyle="outline",
            width=12
        )
        self.select_folder_btn.pack(side="left", padx=(0, 5))
        
        self.select_files_btn = ttk.Button(
            button_frame, 
            text=self.app._("select_files"), 
            command=self.app.browse_input,
            bootstyle="outline-primary",
            width=12
        )
        self.select_files_btn.pack(side="left")
        
        # Hỗ trợ kéo thả
        self.input_entry.drop_target_register(DND_FILES)
        self.input_entry.dnd_bind('<<Drop>>', self.app.handle_drop_input)
        
        # Phần gợi ý kéo thả
        tip_frame = ttk.Frame(input_container)
        tip_frame.pack(fill="x")
        
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
        self.output_frame.pack(fill="x", pady=(0, 15), ipady=5)
        
        # Container cho toàn bộ phần output
        output_container = ttk.Frame(self.output_frame)
        output_container.pack(fill="x", expand=True)
        
        output_group = ttk.Frame(output_container)
        output_group.pack(fill="x", expand=True, pady=(0, 10))
        
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
            bootstyle="outline",
            width=12
        )
        self.output_select_btn.pack(side="right", padx=(10, 0))
        
        # Hỗ trợ kéo thả output
        self.output_entry.drop_target_register(DND_FILES)
        self.output_entry.dnd_bind('<<Drop>>', self.app.handle_drop_output)
        
        # Phần định dạng xuất
        format_frame = ttk.Frame(output_container)
        format_frame.pack(fill="x", pady=(0, 5))
        
        format_label = ttk.Label(
            format_frame, 
            text=f"{self.app._('export_format')}:",
            font=self.app.normal_font
        )
        format_label.pack(side="left", padx=(0, 10))
        
        formats = [".png", ".jpg", ".tif", ".bmp"]
        self.format_combobox = ttk.Combobox(
            format_frame, 
            textvariable=self.app.output_format_var, 
            values=formats,
            state="readonly",
            width=8,
            bootstyle="primary"
        )
        self.format_combobox.pack(side="left")
        self.format_combobox.bind("<<ComboboxSelected>>", self._format_changed)
        
    def _format_changed(self, *args):
        """Xử lý khi người dùng thay đổi định dạng ảnh"""
        # Gọi xử lý trong app nếu cần
        pass 