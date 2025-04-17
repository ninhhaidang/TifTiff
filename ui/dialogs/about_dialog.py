"""
About dialog module for TifTiff application
"""

import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit, 
                           QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from resources.translations import get_translation

# Create an alias for the translation function to match the expected usage
_ = lambda key: get_translation(key)


class AboutDialog(QDialog):
    """Dialog displaying information about the application"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(_("about_title"))
        self.setWindowIcon(QIcon(os.path.join("resources", "icons", "info.png")))
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI components"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(_("app_name"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Version
        version_label = QLabel(f"v{_('app_version')}")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        description = QTextEdit()
        description.setReadOnly(True)
        
        about_text = f"""
        <h3>{_('about_description_title')}</h3>
        <p>{_('about_description')}</p>
        
        <h3>{_('features_title')}</h3>
        <ul>
            <li>{_('feature_image_processing')}</li>
            <li>{_('feature_geo_processing')}</li>
            <li>{_('feature_batch_processing')}</li>
            <li>{_('feature_visualization')}</li>
        </ul>
        
        <h3>{_('developer_info')}</h3>
        <p>{_('developed_by')}</p>
        """
        
        description.setHtml(about_text)
        layout.addWidget(description)
        
        # Buttons
        button_layout = QHBoxLayout()
        close_button = QPushButton(_("close"))
        close_button.clicked.connect(self.close)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout) 