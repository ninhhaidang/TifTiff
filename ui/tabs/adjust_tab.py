"""
Tab điều chỉnh ảnh cho ứng dụng TifTiff
"""

import os
import ttkbootstrap as ttk
from tkinterdnd2 import DND_FILES

from resources.constants import ICONS

class AdjustTab:
    """Tab điều chỉnh ảnh"""
    
    def __init__(self, parent, app):
        """Khởi tạo tab điều chỉnh ảnh"""
        self.parent = parent
        self.app = app
        self.build()
        
    def build(self):
        """Xây dựng giao diện tab"""
        # Tùy chỉnh độ sáng
        brightness_frame = ttk.LabelFrame(self.parent, text=self.app._("adjust_brightness"), padding=10)
        brightness_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        brightness_slider = ttk.Scale(
            brightness_frame,
            from_=0.0,
            to=2.0,
            variable=self.app.brightness_var,
            value=1.0,
            bootstyle="primary"
        )
        brightness_slider.pack(fill="x", pady=5)
        
        brightness_value_frame = ttk.Frame(brightness_frame)
        brightness_value_frame.pack(fill="x")
        
        ttk.Label(brightness_value_frame, text="0.0").pack(side="left")
        ttk.Label(brightness_value_frame, text="1.0").pack(side="left", padx=(180, 180))
        ttk.Label(brightness_value_frame, text="2.0").pack(side="right")
        
        # Tùy chỉnh độ tương phản
        contrast_frame = ttk.LabelFrame(self.parent, text=self.app._("adjust_contrast"), padding=10)
        contrast_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        contrast_slider = ttk.Scale(
            contrast_frame,
            from_=0.0,
            to=2.0,
            variable=self.app.contrast_var,
            value=1.0,
            bootstyle="primary"
        )
        contrast_slider.pack(fill="x", pady=5)
        
        contrast_value_frame = ttk.Frame(contrast_frame)
        contrast_value_frame.pack(fill="x")
        
        ttk.Label(contrast_value_frame, text="0.0").pack(side="left")
        ttk.Label(contrast_value_frame, text="1.0").pack(side="left", padx=(180, 180))
        ttk.Label(contrast_value_frame, text="2.0").pack(side="right")
        
        # Tùy chỉnh độ bão hòa
        saturation_frame = ttk.LabelFrame(self.parent, text=self.app._("adjust_saturation"), padding=10)
        saturation_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        saturation_slider = ttk.Scale(
            saturation_frame,
            from_=0.0,
            to=2.0,
            variable=self.app.saturation_var,
            value=1.0,
            bootstyle="primary"
        )
        saturation_slider.pack(fill="x", pady=5)
        
        saturation_value_frame = ttk.Frame(saturation_frame)
        saturation_value_frame.pack(fill="x")
        
        ttk.Label(saturation_value_frame, text="0.0").pack(side="left")
        ttk.Label(saturation_value_frame, text="1.0").pack(side="left", padx=(180, 180))
        ttk.Label(saturation_value_frame, text="2.0").pack(side="right")
        
        # Reset button
        reset_frame = ttk.Frame(self.parent)
        reset_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            reset_frame,
            text="Reset",
            command=self._reset_adjustments,
            bootstyle="secondary",
            width=15
        ).pack(side="right")
        
    def _reset_adjustments(self):
        """Đặt lại các giá trị điều chỉnh về mặc định"""
        self.app.brightness_var.set("1.0")
        self.app.contrast_var.set("1.0")
        self.app.saturation_var.set("1.0") 