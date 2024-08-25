from styles import (enable, disable, button_styles, level_button_styles, stylize_level_button)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,QHBoxLayout)
from PySide6.QtGui import QFont, QMovie
import asyncio
import pandas as pd
from datetime import datetime
from functools import partial
from DataStreamer import DataStreamer

class TestAndCollectPage(QWidget):
    def __init__(self, switch_page_callback, folder_path, connections):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.folder_path = folder_path
        self.connections = connections
        self.setGeometry(350, 100, 1200, 600)
        layout = QVBoxLayout()

        # start button
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
        enable(self.start_button, button_styles['start/end button enabled'])
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # two paned splitter
        middle_container = QWidget()
        middle_layout = QHBoxLayout(middle_container)
        self.tester = TesterPage(folder_path, connections)
        middle_layout.addWidget(self.tester)
        middle_layout.setStretch(0, 1)
        middle_layout.setStretch(1, 0)
        self.collector = CollectorPage(folder_path, connections)
        middle_layout.addWidget(self.collector)
        layout.addWidget(middle_container)

        # end button
        self.end_button = QPushButton("End")
        self.end_button.clicked.connect(self.end)
        disable(self.end_button, button_styles['start/end button disabled'])
        layout.addWidget(self.end_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def start(self):
        disable(self.start_button, button_styles['start/end button disabled'])
        enable(self.end_button, button_styles['start/end button enabled'])

        self.tester.start()
        self.collector.start()
    
    def end(self):
        disable(self.end_button, button_styles['start/end button disabled'])
        self.tester.end()
        self.collector.end()
        self.connections.closeAll()
        self.switch_page_callback()


class TesterPage(QWidget):
    def __init__(self, folder_path, connections):
        super().__init__()
        container = QWidget()
        container.setStyleSheet("background-color: lightblue;") 
        layout = QVBoxLayout(container)

        self.folder_path = folder_path
        self.connections = connections

        labels_widget = QWidget()
        labels_layout = QVBoxLayout(labels_widget)
        labels_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.numReps = QLabel("Number of Repetitions:")
        self.numReps.setFont(QFont("Comic Sans MS", 30))
        labels_layout.addWidget(self.numReps, alignment=Qt.AlignmentFlag.AlignCenter)

        self.title6 = QLabel("")
        self.title6.setFont( QFont("Comic Sans MS", 45))
        labels_layout.addWidget(self.title6, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(labels_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.robot_label = QLabel()
        self.robot_movie = QMovie("/Users/erinliu/Downloads/1 Muscle Fatigue/xIMU3/Data_Collection/giphy.gif")
        self.robot_label.setMovie(self.robot_movie)
        gif_size = QSize(1200/4, 1000/4)
        self.robot_label.setFixedSize(gif_size)
        self.robot_movie.setScaledSize(gif_size)
        self.robot_movie.start()
        layout.addWidget(self.robot_label, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        self.initiate_plot()

    def initiate_plot(self):
        self.dataStreamer = None
        self.plot_data = []
        self.peaks = []

    def start(self):
        self.wrist_connection = self.connections.get_wrist_connection()
        self.arm_connection = self.connections.get_arm_connection()
        self.dataStreamer = DataStreamer(self.wrist_connection, self.arm_connection)
        self.dataStreamer.peaks = self.peaks
        self.dataStreamer.pitch_data = self.plot_data
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.update_plot)
        self.plot_timer.start(100)  # Update every 100 milliseconds


    def end(self):
        self.dataStreamer.end(self.folder_path)

    def update_plot(self):

        self.numReps.setText(f"Number of Repetitions: {len(self.peaks)}")
        self.title6.setText(f"Prediction: {self.dataStreamer.fatigue}")


class CollectorPage(QWidget):
    def __init__(self, folder_path, connections):
        super().__init__()
        
        container = QWidget()
        layout = QVBoxLayout(container)

        self.folder_path = folder_path
        self.connections = connections

        # add title. When start is clicked, this is where the countdown will appear.
        self.title = QLabel("What is your level of exertion?")
        self.title.setFont(QFont('', 30))
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # initialize internal 10 second countdown timer
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_seconds = 10

        # add subtext. This is where borg logs will appear. 
        self.text = QLabel(f"No logs.")
        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # initiate all level buttons. Disabled on default.
        self.level_buttons = {}
        for level, button_properties in level_button_styles.items():
            button = self.add_level_button(level, button_properties)
            layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            self.level_buttons[button] = button_properties
        self.disable_all_level_buttons()

        # initiate dictionary of borg results
        self.borg = {}
        layout.setSpacing(4)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        self.setLayout(main_layout)
            
    def add_level_button(self, level, button_properties):
        button_text = button_properties['button_text']
        button = QPushButton(text=f"Level {str(level).ljust(6)}\t{button_text}")
        if level < 10:
            button.clicked.connect(partial(self.on_button_click, level))
        else:
            def max_button_click():
                self.log(level)
                self.end()
            button.clicked.connect((max_button_click))
        return button

    def disable_all_level_buttons(self):
        for button, button_properties in self.level_buttons.items():
            text_color = button_properties['text_color']
            background_color = button_properties['background_color']
            disable(button, styles=stylize_level_button(background_color, text_color, enabled=False))

    def enable_all_level_buttons(self):
        for button, button_properties in self.level_buttons.items():
            text_color = button_properties['text_color']
            background_color = button_properties['background_color']
            enable(button, styles=stylize_level_button(background_color, text_color, enabled=True))

    def on_button_click(self, level):
        asyncio.create_task(self.click(level))

    def start_countdown(self):
        self.countdown_seconds = 5
        self.title.setText(f"{self.countdown_seconds} seconds")
        self.countdown_timer.start(1000)
    
    def update_countdown(self):
        self.countdown_seconds -= 1
        if self.countdown_seconds > 1:
            self.title.setText(f"{self.countdown_seconds} seconds")
        elif self.countdown_seconds == 1:
            self.title.setText(f"{self.countdown_seconds} second")
        else:
            self.countdown_timer.stop()
            self.title.setText("What is your level of exertion?")

    def log(self, level):
        """
        Logs the timestamp in the borg scale with the argument fatigue level
        """
        timestamp = datetime.now()
        self.borg[timestamp] = level
        display_text = f"Logged {level} at {timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]}"
        print(display_text)
        self.text.setText(display_text)

    async def click(self, level):
        """
        Triggered when any of the level buttons are clicked.
        - logs the specified level into the borg scale
        - starts a 20 second countdown
        """
        await asyncio.sleep(0)
        self.log(level)
        self.start_countdown()

    def start(self):
        """
        Triggered when start button is clicked.
        - disables the start button and enables all other buttons
        - records a 0 to the borg scale to represent the start of data collection
        - starts logging from the IMUs
        - starts the 20 second countdown
        """
        self.enable_all_level_buttons()
        self.log(0)
        self.start_countdown()

    def end(self):
        """
        Triggered when the end button is clicked.
        - disables all buttons
        - stops the countdown timer
        - saves the IMU data logger results
        - saves the borg scale results
        """
        self.countdown_timer.stop()
        df = pd.DataFrame.from_dict(self.borg, orient='index', columns=['fatigue'])
        csv_filename = f"{self.folder_path}/borg.csv"
        df.to_csv(csv_filename, index=True)