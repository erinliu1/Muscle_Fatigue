from helpers import create_new_folder
from Setup import SetupPage
from BasicInformation import BasicInformationPage
from Collector import TestAndCollectPage
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
        
        # creating page 1
        self.page1 = SetupPage(self.go_to_page2)
        self.stacked_widget.addWidget(self.page1)
        self.stacked_widget.setCurrentWidget(self.page1)


    def go_to_page2(self, connections):
        self.connections = connections

        # creating page 2
        directory = '/Users/erinliu/Downloads/1 Muscle Fatigue/xIMU3/Data_Collection/Test Data'
        folder_name = 'participant'
        folder_path = create_new_folder(directory, folder_name)
        
        self.page2 = BasicInformationPage(self.go_to_page3, folder_path)
        self.stacked_widget.addWidget(self.page2)
        self.stacked_widget.setCurrentWidget(self.page2)



    def go_to_page3(self, folder_path):
        self.folder_path = folder_path

        # creating page 3
        self.page3 = TestAndCollectPage(self.go_to_page4, folder_path, self.connections)
        self.stacked_widget.addWidget(self.page3)
        self.stacked_widget.setCurrentWidget(self.page3)

    
    def go_to_page4(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    QtAsyncio.run()