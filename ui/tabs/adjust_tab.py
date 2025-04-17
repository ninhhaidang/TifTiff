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
        
    def update_language(self):
        """Cập nhật ngôn ngữ cho tất cả các thành phần"""
        if hasattr(self, 'bg_frame'):
            self.bg_frame.config(text=self.app._("bg_options"))
            
        if hasattr(self, 'remove_black_check'):
            self.remove_black_check.config(text=self.app._("remove_black"))
            
        if hasattr(self, 'remove_white_check'):
            self.remove_white_check.config(text=self.app._("remove_white"))
            
        if hasattr(self, 'brightness_frame'):
            self.brightness_frame.config(text=self.app._("adjust_brightness"))
            
        if hasattr(self, 'contrast_frame'):
            self.contrast_frame.config(text=self.app._("adjust_contrast"))
            
        if hasattr(self, 'saturation_frame'):
            self.saturation_frame.config(text=self.app._("adjust_saturation"))
        
        if hasattr(self, 'scale_labelframe'):
            self.scale_labelframe.config(text=f"📏 {self.app._('scale_ratio')}")
        
    def build(self):
        """Xây dựng giao diện tab"""
        # Tỷ lệ kích thước
        scale_frame = ttk.Frame(self.parent)
        scale_frame.pack(fill="x", pady=(0, 10))
        
        # Tạo LabelFrame cho phần điều chỉnh tỷ lệ
        self.scale_labelframe = ttk.LabelFrame(
            scale_frame, 
            text=f"📏 {self.app._('scale_ratio')}", 
            padding=10
        )
        self.scale_labelframe.pack(fill="x", ipady=5)
        
        # Thêm thanh trượt cho tỷ lệ
        scale_control_frame = ttk.Frame(self.scale_labelframe)
        scale_control_frame.pack(fill="x")
        
        self.scale_slider = ttk.Scale(
            scale_control_frame,
            from_=0.1,
            to=4.0,
            value=float(self.app.scale_ratio_var.get()),
            command=self._update_scale_value,
            bootstyle="primary"
        )
        self.scale_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.scale_entry = ttk.Entry(
            scale_control_frame,
            textvariable=self.app.scale_ratio_var,
            width=6
        )
        self.scale_entry.pack(side="right")
        self.scale_entry.bind("<Return>", self._entry_scale_changed)
        self.scale_entry.bind("<FocusOut>", self._entry_scale_changed)
        
        ttk.Label(
            scale_control_frame,
            text="×",
            font=self.app.normal_font
        ).pack(side="right", padx=(0, 5))
        
        # Các preset tỷ lệ phổ biến
        preset_frame = ttk.Frame(self.scale_labelframe)
        preset_frame.pack(fill="x", pady=(10, 0))
        
        preset_sizes = ["0.25", "0.5", "1.0", "1.5", "2.0", "3.0", "4.0"]
        
        for preset in preset_sizes:
            btn_text = f"{preset}×"
            ttk.Button(
                preset_frame,
                text=btn_text,
                command=lambda p=preset: self._set_scale(p),
                width=5,
                bootstyle="secondary-outline"
            ).pack(side="left", padx=(0, 5))
        
        # Tùy chọn nền
        self.bg_frame = ttk.LabelFrame(self.parent, text=self.app._("bg_options"), padding=10)
        self.bg_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        self.remove_black_check = ttk.Checkbutton(
            self.bg_frame, 
            text=self.app._("remove_black"), 
            variable=self.app.remove_black_bg,
            bootstyle="success"
        )
        self.remove_black_check.pack(anchor="w", pady=(0, 5))
        
        self.remove_white_check = ttk.Checkbutton(
            self.bg_frame, 
            text=self.app._("remove_white"), 
            variable=self.app.remove_white_bg,
            bootstyle="success"
        )
        self.remove_white_check.pack(anchor="w")
        
        # Tùy chỉnh độ sáng
        self.brightness_frame = ttk.LabelFrame(self.parent, text=self.app._("adjust_brightness"), padding=10)
        self.brightness_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        brightness_slider = ttk.Scale(
            self.brightness_frame,
            from_=0.0,
            to=2.0,
            variable=self.app.brightness_var,
            value=1.0,
            bootstyle="primary"
        )
        brightness_slider.pack(fill="x", pady=5)
        
        brightness_value_frame = ttk.Frame(self.brightness_frame)
        brightness_value_frame.pack(fill="x")
        
        ttk.Label(brightness_value_frame, text="0.0").pack(side="left")
        ttk.Label(brightness_value_frame, text="1.0").pack(side="left", padx=(180, 180))
        ttk.Label(brightness_value_frame, text="2.0").pack(side="right")
        
        # Tùy chỉnh độ tương phản
        self.contrast_frame = ttk.LabelFrame(self.parent, text=self.app._("adjust_contrast"), padding=10)
        self.contrast_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        contrast_slider = ttk.Scale(
            self.contrast_frame,
            from_=0.0,
            to=2.0,
            variable=self.app.contrast_var,
            value=1.0,
            bootstyle="primary"
        )
        contrast_slider.pack(fill="x", pady=5)
        
        contrast_value_frame = ttk.Frame(self.contrast_frame)
        contrast_value_frame.pack(fill="x")
        
        ttk.Label(contrast_value_frame, text="0.0").pack(side="left")
        ttk.Label(contrast_value_frame, text="1.0").pack(side="left", padx=(180, 180))
        ttk.Label(contrast_value_frame, text="2.0").pack(side="right")
        
        # Tùy chỉnh độ bão hòa
        self.saturation_frame = ttk.LabelFrame(self.parent, text=self.app._("adjust_saturation"), padding=10)
        self.saturation_frame.pack(fill="x", pady=(0, 10), ipady=5)
        
        saturation_slider = ttk.Scale(
            self.saturation_frame,
            from_=0.0,
            to=2.0,
            variable=self.app.saturation_var,
            value=1.0,
            bootstyle="primary"
        )
        saturation_slider.pack(fill="x", pady=5)
        
        saturation_value_frame = ttk.Frame(self.saturation_frame)
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
        
    def _update_scale_value(self, value):
        """Cập nhật giá trị tỷ lệ khi di chuyển thanh trượt"""
        # Cập nhật giá trị trong entry
        self.app.scale_ratio_var.set(f"{float(value):.2f}")
        
    def _entry_scale_changed(self, event):
        """Xử lý khi người dùng nhập giá trị tỷ lệ scale"""
        try:
            value = float(self.app.scale_ratio_var.get())
            # Giới hạn trong khoảng hợp lệ
            if value < 0.1:
                value = 0.1
            elif value > 4.0:
                value = 4.0
                
            # Cập nhật lại giá trị đã được kiểm tra
            self.app.scale_ratio_var.set(f"{value:.2f}")
            
            # Cập nhật vị trí thanh trượt
            self.scale_slider.set(value)
        except ValueError:
            # Nếu nhập giá trị không hợp lệ, trở về 1.0
            self.app.scale_ratio_var.set("1.00")
            self.scale_slider.set(1.0)
            
    def _set_scale(self, value):
        """Thiết lập tỷ lệ từ preset"""
        self.app.scale_ratio_var.set(value)
        self.scale_slider.set(float(value)) 