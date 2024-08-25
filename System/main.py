import os
from SetupPage import SetupPage
from BasicInformationPage import BasicInformationPage
from TestAndCollectPage import TestAndCollectPage
from PySide6.QtWidgets import (QApplication, QMainWindow, QStackedWidget)
import PySide6.QtAsyncio as QtAsyncio
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Online Fatigue Model")
        self.showFullScreen()
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # creating page 1 : Connections Setup Page
        self.page1 = SetupPage(self.go_to_page2)
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.setCurrentWidget(self.page1)


    def go_to_page2(self, connections):
        self.connections = connections

        # creating page 2 : Basic Information Page
        directory = './Data/Participants'
        folder_name = 'individual'
        folder_path = self.create_new_folder(directory, folder_name)
        
        self.page2 = BasicInformationPage(self.go_to_page3, folder_path)
        self.stacked_widget.addWidget(self.page2)
        self.stacked_widget.setCurrentWidget(self.page2)



    def go_to_page3(self, folder_path):
        self.folder_path = folder_path

        # creating page 3 : Model Test / Data Collection Page
        self.page3 = TestAndCollectPage(self.close, folder_path, self.connections)
        self.stacked_widget.addWidget(self.page3)
        self.stacked_widget.setCurrentWidget(self.page3)
        

    def create_new_folder(self, directory, folder_name):
        """
        Create a new folder with leading zeros in the folder name.
        """
        existing_folders = [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]

        if not existing_folders:
            new_folder_name = f"{folder_name}_00"
        else:
            last_numbers = [int(name.split('_')[-1]) for name in existing_folders if name.split('_')[-1].isdigit()]
            max_last_number = max(last_numbers) if last_numbers else 0
            
            new_last_number = max_last_number + 1

            # Generate folder name with leading zeros
            new_folder_name = f"{folder_name}_{new_last_number:02d}"

        folder_path = os.path.join(directory, new_folder_name)
        os.makedirs(folder_path)
        return folder_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    QtAsyncio.run()