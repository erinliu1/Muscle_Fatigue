import ximu3

class DataLogger():
    """
    Wrapper class for the xIMU3 DataLogger object
    """
    def __init__(self, folder_path, folder_name, connectionsList):
        self.connectionsList = connectionsList
        if not connectionsList.checkOpenAll():
            connectionsList.openAll()
        self.data_logger = ximu3.DataLogger(folder_path, folder_name, self.connectionsList.get_connections())
        print(self.data_logger)
    
    def start(self):
        self.result = self.data_logger.get_result()
        if self.result != ximu3.RESULT_OK:
            print("There was an error logging your results.")
        else:
            print("xIMU successfully started logging")

    def stop_and_save(self):
        del self.data_logger # saves the data
        if self.result != ximu3.RESULT_OK:
            print("There was an error logging your results.")
        else:
            print("Data logger results have been saved")
