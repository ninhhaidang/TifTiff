"""
Tab nhật ký cho ứng dụng TifTiff
"""

import os
import tkinter as tk
from tkinter import END
import ttkbootstrap as ttk
from tkinterdnd2 import DND_FILES

from resources.constants import ICONS
from utils.logger import logger

class LogTab:
    """Tab nhật ký"""
    
    def __init__(self, parent, app):
        """Khởi tạo tab nhật ký"""
        self.parent = parent
        self.app = app
        self.build()
        
    def build(self):
        """Xây dựng giao diện tab"""
        log_frame = ttk.Frame(self.parent)
        log_frame.pack(fill="both", expand=True)
        
        # Xác định màu nền dựa trên chủ đề
        bg_color = "#f7f7f7" if not self.app.is_dark_mode.get() else "#2a2a2a"
        fg_color = "#000000" if not self.app.is_dark_mode.get() else "#ffffff"
        
        self.log_text = tk.Text(
            log_frame, 
            wrap="word", 
            font=("Consolas", 10), 
            bg=bg_color,
            fg=fg_color,
            relief="flat"
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Thêm nút xóa nhật ký
        button_frame = ttk.Frame(self.parent)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text=self.app._("clear_log"),
            command=self.clear_log,
            bootstyle="danger-outline",
            width=15
        ).pack(side="right")
        
        # Thiết lập logger
        self.app.logger.set_text_widget(self.log_text)
        
        # Tự động thêm tiêu đề
        self.app.logger.log(f"TifTiff - {self.app._('version')} 1.1\n{'-'*40}")
        self.app.logger.log(f"{self.app._('ready')}")
        
    def clear_log(self):
        """Xóa nội dung nhật ký"""
        self.log_text.delete(1.0, END) 