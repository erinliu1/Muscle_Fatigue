import os
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QWidget, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox)
from PySide6.QtGui import QFont
import pandas as pd
from styles import button_styles


class BasicInformationPage(QWidget):
    def __init__(self, switch_page_callback, folder_path):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.folder_path = folder_path
        layout = QVBoxLayout()

        self.title = QLabel("Basic Information")
        title_font = QFont()
        title_font.setPointSize(50)
        self.title.setFont(title_font)
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.directions = QLabel("Please enter the following information:")
        directions_font = QFont()
        directions_font.setPointSize(20)
        self.directions.setFont(directions_font)
        layout.addWidget(self.directions, alignment=Qt.AlignmentFlag.AlignCenter)

        form_layout = QFormLayout()

        form_font = QFont()
        form_font.setPointSize(18)
        min_height = 40
        min_width = 400

        def add_form_element(label, input):
            input.setFont(form_font)
            input.setMinimumHeight(min_height)
            input.setMinimumWidth(min_width)
            label.setFont(form_font)
            label.setMinimumHeight(min_height)
            form_layout.addRow(label, input)

        
        # Age input
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 120)
        age_label = QLabel("Age:")
        add_form_element(age_label, self.age_input)

        
        # Height input
        self.height_input = QSpinBox()
        self.height_input.setRange(0, 300)
        self.height_input.setSuffix(" cm")
        height_label = QLabel("Height:")
        add_form_element(height_label, self.height_input)

        
        # Weight input
        self.weight_input = QSpinBox()
        self.weight_input.setRange(0, 500)
        self.weight_input.setSuffix(" kg")
        weight_label = QLabel("Weight:")
        add_form_element(weight_label, self.weight_input)

        
        # Gender input
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        gender_label = QLabel("Gender:")
        add_form_element(gender_label, self.gender_input)


        # Dumbbell input
        self.dumbbell_input = QDoubleSpinBox()
        self.dumbbell_input.setRange(0, 500)
        self.dumbbell_input.setSuffix(" kg")
        dumbbell_label = QLabel("Dumbbell Weight:")
        add_form_element(dumbbell_label, self.dumbbell_input)

        # Dominant arm input
        self.dominant_arm_input = QComboBox()
        self.dominant_arm_input.addItems(["Dominant", "Non-dominant"])
        dominant_arm_label = QLabel("Which arm are you using?")
        add_form_element(dominant_arm_label, self.dominant_arm_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setStyleSheet(button_styles['submit button'])
        layout.addWidget(self.submit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        
    def on_submit(self):
        df = pd.DataFrame({
            'age': [self.age_input.text()],
            'height': [self.height_input.text()],
            'weight': [self.weight_input.text()],
            'gender': [self.gender_input.currentText()],
            'dumbbell': [self.dumbbell_input.text()],
            'dominant arm': [self.dominant_arm_input.currentText()],
        })

        os.makedirs(f"{self.folder_path}/{self.dominant_arm_input.currentText()}")
        csv_filename = f"{self.folder_path}/{self.dominant_arm_input.currentText()}/basic_info.csv"
        df.to_csv(csv_filename, index=False)
        self.switch_page_callback(f"{self.folder_path}/{self.dominant_arm_input.currentText()}")
