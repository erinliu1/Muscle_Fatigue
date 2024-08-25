import ximu3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout)
from styles import (enable, disable, button_styles)
from ConnectionSetup import (Connection, ConnectionList)
from PySide6.QtGui import QFont

class SetupPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        layout = QVBoxLayout()

        self.devices = None

        # add title
        self.title = QLabel("Set up connections")
        self.title.setFont(QFont('', 50))
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # initialize search for IMUs button
        self.imu_button = QPushButton("Search for IMUs")
        self.imu_button.clicked.connect(self.search_for_IMUs)
        self.imu_button.setStyleSheet(button_styles['imu button'])
        layout.addWidget(self.imu_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.imu_label = QLabel("")
        self.imu_label.setFont(QFont('', 20))
        layout.addWidget(self.imu_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.on_continue)
        disable(self.continue_button, button_styles['continue button disabled'])
        layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.on_skip)
        layout.addWidget(self.skip_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
    
    def search_for_IMUs(self):
        if not self.devices:
            self.devices = ximu3.NetworkAnnouncement().get_messages_after_short_delay()
            if not self.devices: 
                display_text = "No IMUs found. Make sure you're using the correct WiFi."
            else:
                display_text = "Found the following devices:\n"
                myConnectionList = []
                for device in self.devices:
                    connection = Connection(device)
                    myConnectionList.append(connection)
                    display_text += f"    {str(connection)}\n"
                enable(self.continue_button, button_styles['continue button enabled'])
                self.connections = ConnectionList(myConnectionList)
            self.imu_label.setText(display_text)

    def on_continue(self):
        self.switch_page_callback(self.connections)

    def on_skip(self):
        self.switch_page_callback(ConnectionList([]))