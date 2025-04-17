"""
Các hằng số và dữ liệu tĩnh cho ứng dụng TifTiff
"""

import os
import sys
from PIL import Image

# ✅ Hàm này giúp lấy đường dẫn file đúng cả khi chạy .py và .exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller tạo ra khi đóng gói
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Đường dẫn file cấu hình
CONFIG_FILE = "config.json"

# Các ngôn ngữ hỗ trợ
LANGUAGES = {
    "vi": "Tiếng Việt",
    "en": "English"
}

# Danh sách các hệ tọa độ phổ biến
COMMON_CRS = {
    "WGS 84 (EPSG:4326)": "EPSG:4326",
    "Web Mercator (EPSG:3857)": "EPSG:3857",
    "UTM Zone 48N - VN (EPSG:32648)": "EPSG:32648",
    "UTM Zone 49N - VN (EPSG:32649)": "EPSG:32649",
    "VN-2000 (EPSG:9210)": "EPSG:9210"
}

# Danh sách các chủ đề
THEMES = {
    "cosmo": "Cosmo (Light)",
    "flatly": "Flatly (Light)",
    "minty": "Minty (Light)",
    "darkly": "Darkly (Dark)",
    "superhero": "Superhero (Dark)",
    "solar": "Solar (Dark)"
}

# Các biểu tượng cho UI
ICONS = {
    "input": "📂",           # File input
    "output": "📤",          # File output
    "convert": "🔄",         # Convert/process
    "settings": "⚙️",        # Settings
    "options": "🔧",         # Options
    "adjust": "🎨",          # Image adjustments
    "geo": "🌐",             # Geospatial
    "info": "📝",            # Log/info
    "presentation": "📊",    # Presentation mode
    "research": "🔬",        # Research mode 
    "detected_crs": "🔎",    # Detected CRS
    "source_crs": "🌍",      # Source CRS
    "target_crs": "🎯",      # Target CRS
    "progress": "📈",        # Progress
    "geo_export": "🗺️",      # Geo export
    "geo_guide": "ℹ️",       # Geo info
    "help": "❓",            # Help
    "success": "✅",         # Success
    "warning": "⚠️",         # Warning
    "error": "❌",           # Error
    "theme": "🎭",           # Theme
    "language": "🌍"         # Language
}

# Cài đặt cho PIL
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.ANTIALIAS 