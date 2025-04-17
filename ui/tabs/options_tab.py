"""
Tab tùy chọn cho ứng dụng TifTiff
"""

import os
import ttkbootstrap as ttk
from tkinterdnd2 import DND_FILES

from resources.constants import ICONS, THEMES, LANGUAGES

class OptionsTab:
    """Tab tùy chọn xử lý ảnh"""
    
    def __init__(self, parent, app):
        """Khởi tạo tab tùy chọn"""
        self.parent = parent
        self.app = app
        self.build()
        
    def build(self):
        """Xây dựng giao diện tab"""
        # Tùy chọn nền
        bg_frame = ttk.LabelFrame(self.parent, text=self.app._("bg_options"), padding=10)
        bg_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        ttk.Checkbutton(
            bg_frame, 
            text=self.app._("remove_black"), 
            variable=self.app.remove_black_bg,
            bootstyle="success"
        ).pack(anchor="w", pady=(0, 5))
        
        ttk.Checkbutton(
            bg_frame, 
            text=self.app._("remove_white"), 
            variable=self.app.remove_white_bg,
            bootstyle="success"
        ).pack(anchor="w")
        
        # Phần chủ đề và ngôn ngữ
        appearance_frame = ttk.LabelFrame(self.parent, text=self.app._("appearance"), padding=10)
        appearance_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        # Chọn chủ đề
        theme_frame = ttk.Frame(appearance_frame)
        theme_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(theme_frame, text=f"{ICONS['theme']} {self.app._('theme')}:").pack(side="left")
        ttk.OptionMenu(
            theme_frame,
            self.app.theme_var,
            self.app.theme_var.get(),
            *THEMES.keys(),
            bootstyle="primary"
        ).pack(side="left", padx=(5, 0), fill="x", expand=True)
        
        # Chọn ngôn ngữ
        lang_frame = ttk.Frame(appearance_frame)
        lang_frame.pack(fill="x")
        
        ttk.Label(lang_frame, text=f"{ICONS['language']} {self.app._('language')}:").pack(side="left")
        ttk.OptionMenu(
            lang_frame,
            self.app.language_var,
            self.app.language_var.get(),
            *LANGUAGES.keys(),
            bootstyle="primary"
        ).pack(side="left", padx=(5, 0), fill="x", expand=True)
        
        # Thêm tùy chọn xuất metadata
        metadata_frame = ttk.LabelFrame(self.parent, text=self.app._("metadata_export"), padding=10)
        metadata_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        button_frame = ttk.Frame(metadata_frame)
        button_frame.pack(fill="x", pady=(5, 0))
        
        ttk.Button(
            button_frame,
            text=self.app._("export_csv"),
            command=lambda: self.app.export_metadata("csv"),
            bootstyle="info-outline",
            width=15
        ).pack(side="left", padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text=self.app._("export_json"),
            command=lambda: self.app.export_metadata("json"),
            bootstyle="info-outline",
            width=15
        ).pack(side="left")
        
        # Phần thông tin về phiên bản
        version_frame = ttk.Frame(self.parent)
        version_frame.pack(fill="x", side="bottom", pady=(20, 0))
        
        ttk.Label(
            version_frame,
            text="TifTiff v1.1 - © 2023",
            font=("Segoe UI", 8),
            foreground="#888888"
        ).pack(side="right") 