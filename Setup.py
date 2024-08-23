import ximu3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, QPushButton, QVBoxLayout)
from styles import (continue_button_style_enabled,continue_button_style_disabled,imu_button_style)
from AbstractWidget import AbstractWidget
from ConnectionSetup import (Connection, ConnectionList)

class SetupPage(AbstractWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        layout = QVBoxLayout()

        # add title
        self.title = QLabel("Set up connections")
        self.title.setFont(super().set_font_size(50))
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # initialize search for IMUs button
        self.imu_button = QPushButton("Search for IMUs")
        self.imu_button.clicked.connect(self.search_for_IMUs)
        self.imu_button.setStyleSheet(imu_button_style)
        layout.addWidget(self.imu_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # add label that shows whether IMUs are successfully connected 
        self.imu_label = QLabel("")
        self.imu_label.setFont(super().set_font_size(20))
        layout.addWidget(self.imu_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # add continue button that takes you to next page. disabled on default, enabled when imus are connected.
        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.on_continue)
        self.disable(self.continue_button, continue_button_style_disabled)
        layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.skip_button = QPushButton("Skip")
        self.skip_button.clicked.connect(self.on_skip)
        layout.addWidget(self.skip_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
    
    def search_for_IMUs(self):
        devices = ximu3.NetworkAnnouncement().get_messages_after_short_delay()
        if not devices: 
            display_text = "No IMUs found. Make sure you're using the correct WiFi."
        else:
            display_text = "Found the following devices:\n"
            myConnectionList = []
            for device in devices:
                connection = Connection(device)
                myConnectionList.append(connection)
                display_text += f"    {str(connection)}\n"
            self.enable(self.continue_button, continue_button_style_enabled)
            self.connections = ConnectionList(myConnectionList)
        self.imu_label.setText(display_text)

    def on_continue(self):
        self.switch_page_callback(self.connections)

    def on_skip(self):
        self.switch_page_callback(ConnectionList([]))