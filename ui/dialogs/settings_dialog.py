"""
Hộp thoại cài đặt chung cho ứng dụng TifTiff
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from resources.constants import ICONS, THEMES, LANGUAGES

class SettingsDialog:
    """Hộp thoại cài đặt với các tùy chọn chung"""
    
    def __init__(self, parent, app):
        """Khởi tạo hộp thoại cài đặt"""
        self.parent = parent
        self.app = app
        self.dialog = None
        
        # Lưu các giá trị ban đầu
        self.original_theme = self.app.theme_var.get()
        self.original_language = self.app.language_var.get()
        
        # Tạo các biến tạm thời
        self.temp_theme_var = tk.StringVar(value=self.app.theme_var.get())
        self.temp_language_var = tk.StringVar(value=self.app.language_var.get())
        
        # Tạo và hiển thị hộp thoại
        self._create_dialog()
        
    def _create_dialog(self):
        """Tạo giao diện hộp thoại cài đặt"""
        # Tạo cửa sổ dialog kiểu hộp thoại
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.app._("settings_title"))
        self.dialog.geometry("450x400")
        self.dialog.minsize(400, 350)
        
        # Thiết lập là cửa sổ modal (chặn tương tác với cửa sổ chính)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Thiết lập ở giữa cửa sổ chính
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.parent.winfo_width() - width) // 2 + self.parent.winfo_x()
        y = (self.parent.winfo_height() - height) // 2 + self.parent.winfo_y()
        self.dialog.geometry("+{}+{}".format(x, y))
        
        # Đặt icon cho cửa sổ dialog
        try:
            from resources.constants import resource_path
            self.dialog.iconbitmap(resource_path("icon.ico"))
        except Exception:
            pass
            
        # Tạo frame chính
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Tiêu đề hộp thoại
        header_label = ttk.Label(
            main_frame, 
            text=f"{ICONS['options']} {self.app._('settings_title')}", 
            font=("Segoe UI", 12, "bold")
        )
        header_label.pack(anchor="w", pady=(0, 20))
        
        # Frame chứa các tùy chọn
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill="both", expand=True)
        
        # Phần Appearance
        appearance_frame = ttk.LabelFrame(
            options_frame, 
            text=f"{ICONS['theme']} {self.app._('appearance')}", 
            padding=10
        )
        appearance_frame.pack(fill="x", pady=(0, 15))
        
        # Chọn chủ đề
        theme_frame = ttk.Frame(appearance_frame)
        theme_frame.pack(fill="x", pady=(5, 10))
        
        ttk.Label(
            theme_frame, 
            text=f"{self.app._('theme')}:", 
            width=15
        ).pack(side="left")
        
        theme_menu = ttk.OptionMenu(
            theme_frame,
            self.temp_theme_var,
            self.temp_theme_var.get(),
            *THEMES.keys()
        )
        theme_menu.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Mô tả theme
        theme_desc_frame = ttk.Frame(appearance_frame)
        theme_desc_frame.pack(fill="x")
        
        ttk.Label(
            theme_desc_frame,
            text=" " * 16,  # Khoảng trống tương ứng width của label trên
            width=15
        ).pack(side="left")
        
        self.theme_desc = ttk.Label(
            theme_desc_frame,
            text=THEMES.get(self.temp_theme_var.get(), ""),
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.theme_desc.pack(side="left", fill="x", padx=(10, 0))
        
        # Cập nhật mô tả theme khi thay đổi
        self.temp_theme_var.trace_add("write", self._update_theme_desc)
        
        # Phần Language
        language_frame = ttk.LabelFrame(
            options_frame, 
            text=f"{ICONS['language']} {self.app._('language')}", 
            padding=10
        )
        language_frame.pack(fill="x")
        
        # Chọn ngôn ngữ
        lang_frame = ttk.Frame(language_frame)
        lang_frame.pack(fill="x", pady=5)
        
        ttk.Label(
            lang_frame, 
            text=f"{self.app._('language')}:", 
            width=15
        ).pack(side="left")
        
        lang_menu = ttk.OptionMenu(
            lang_frame,
            self.temp_language_var,
            self.temp_language_var.get(),
            *LANGUAGES.keys()
        )
        lang_menu.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Mô tả ngôn ngữ
        lang_desc_frame = ttk.Frame(language_frame)
        lang_desc_frame.pack(fill="x")
        
        ttk.Label(
            lang_desc_frame,
            text=" " * 16,
            width=15
        ).pack(side="left")
        
        self.lang_desc = ttk.Label(
            lang_desc_frame,
            text=LANGUAGES.get(self.temp_language_var.get(), ""),
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.lang_desc.pack(side="left", fill="x", padx=(10, 0))
        
        # Cập nhật mô tả ngôn ngữ khi thay đổi
        self.temp_language_var.trace_add("write", self._update_lang_desc)
        
        # Frame chứa các nút
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Nút OK, Apply, Cancel
        ttk.Button(
            button_frame,
            text=self.app._("btn_cancel"),
            command=self._cancel,
            bootstyle=SECONDARY,
            width=10
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text=self.app._("btn_apply"),
            command=self._apply,
            bootstyle=INFO,
            width=10
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text=self.app._("btn_ok"),
            command=self._ok,
            bootstyle=SUCCESS,
            width=10
        ).pack(side="right")
        
        # Phiên bản
        version_label = ttk.Label(
            main_frame,
            text="TifTiff v1.1 - © 2025",
            font=("Segoe UI", 8),
            foreground="gray"
        )
        version_label.pack(side="left", pady=(10, 0))
        
    def _update_theme_desc(self, *args):
        """Cập nhật mô tả chủ đề khi thay đổi"""
        self.theme_desc.config(text=THEMES.get(self.temp_theme_var.get(), ""))
        
    def _update_lang_desc(self, *args):
        """Cập nhật mô tả ngôn ngữ khi thay đổi"""
        self.lang_desc.config(text=LANGUAGES.get(self.temp_language_var.get(), ""))
        
    def _apply(self):
        """Áp dụng các thay đổi mà không đóng hộp thoại"""
        # Lưu các giá trị mới
        self.app.theme_var.set(self.temp_theme_var.get())
        self.app.language_var.set(self.temp_language_var.get())
        
        # Cập nhật lại giá trị ban đầu để hủy không hoàn tác những thay đổi đã áp dụng
        self.original_theme = self.temp_theme_var.get()
        self.original_language = self.temp_language_var.get()
        
    def _ok(self):
        """Áp dụng các thay đổi và đóng hộp thoại"""
        self._apply()
        self.dialog.destroy()
        
    def _cancel(self):
        """Hủy các thay đổi và đóng hộp thoại"""
        # Khôi phục các giá trị ban đầu
        self.app.theme_var.set(self.original_theme)
        self.app.language_var.set(self.original_language)
        
        # Đóng hộp thoại
        self.dialog.destroy() 