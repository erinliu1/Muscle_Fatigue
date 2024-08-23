from PySide6.QtWidgets import (QWidget, QLabel)
from PySide6.QtGui import QFont


class AbstractWidget(QWidget):
    def __init__(self):
        super().__init__()

    def set_font_size(self, size):
        font = QFont()
        font.setPointSize(size)
        return font
    
    def add_space(self, size, layout):
        space = QLabel("")
        space.setFont(self.set_font_size(size))
        layout.addWidget(space)

    def enable(self, button, styles=None):
        button.setEnabled(True)
        if styles:
            button.setStyleSheet(styles)
    
    def disable(self, button, styles=None):
        button.setEnabled(False)
        if styles:
            button.setStyleSheet(styles)
    