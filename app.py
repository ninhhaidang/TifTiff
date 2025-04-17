"""
Điểm khởi chạy chính cho ứng dụng TifTiff
"""

import os
import sys
from tkinterdnd2 import TkinterDnD
import ttkbootstrap as ttk

# Thêm thư mục hiện tại vào sys.path để hỗ trợ imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Sử dụng imports phù hợp với cấu trúc thư mục hiện tại
from ui.main_window import MainWindow
from resources.constants import resource_path

def main():
    """Hàm chính để khởi chạy ứng dụng"""
    # Tạo cửa sổ chính với hỗ trợ kéo thả
    root = TkinterDnD.Tk()
    
    # Thiết lập style mặc định
    style = ttk.Style("cosmo")  # hoặc flatly, minty, darkly...
    
    # Thiết lập icon
    try:
        if os.path.exists(resource_path("icon.ico")):
            root.iconbitmap(resource_path("icon.ico"))
    except Exception:
        pass
    
    # Khởi tạo và chạy ứng dụng
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 