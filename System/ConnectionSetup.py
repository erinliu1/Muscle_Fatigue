import ast
import ximu3

class ConnectionList():
    """
    Takes in a list of Connection class objects
    """
    def __init__(self, connectionsList):
        self.connectionsList = connectionsList
    
    def get_connections(self):
        return [x.get_connection_object() for x in self.connectionsList]
    
    def get_wrist_connection(self):
        for connection in self.connectionsList:
            if connection.wrist_or_arm() == 'wrist':
                return connection.get_connection_object()
        print('No wrist connection found.')

    def get_arm_connection(self):
        for connection in self.connectionsList:
            if connection.wrist_or_arm() == 'arm':
                return connection.get_connection_object()
        print('No arm connection found.')
            
    def checkOpenAll(self):
        for connection in self.connectionsList:
            if connection.connection_status != 'Open':
                return False
        return True

    def openAll(self):
        for connection in self.connectionsList:
            connection.open()
    
    def closeAll(self):
        for connection in self.connectionsList:
            connection.close()

class Connection():
    """
    Class which takes in an xIMU3 device and opens a connection through UDP protocol.
    """
    def __init__(self, device):
        self.device = device
        self.device_name = self.device.device_name
        self.serial_number = self.device.serial_number
        self.protocol = None
        self.connection = None
        self.connection_status = None
        self.connectivity_message = "no connections attempted"
        if self.connect():
            self.set_color({'violet_IMU': '#5900FF', 'green_IMU': '#33FF00'}[self.device_name])

    def connect(self):
        """
        Tries to establish a connection with the device using UDP protocol. 
        Returns true if the attempt was successful, false otherwise.
        """
        self.protocol = 'UDP'
        self.connection = ximu3.Connection(self.device.to_udp_connection_info())
        if self.open(): 
            return True

        self.protocol = None
        self.connection = None
        self.connectivity_message = 'failed to connect with UDP'
        return False

    def open(self):
        """
        Tries to open the connection object associated with this device.
        """
        if self.connection == None:
            print("No connection to this device has been established.")
            return False
        if self.connection_status == "Open":
            print(f'{self.protocol} connection is already open in this device.')
            return False
        if self.connection.open() == ximu3.RESULT_OK:
            self.connection_status = "Open"
            self.connectivity_message = f'connected successfully with {self.protocol}'
            print(self.__str__())
            return True
        return False
       
    def close(self):
        """
        Tries to closes the connection object associated with this device.
        """
        if self.connection == None:
            print("No connection to this device has been established.")
            return False
        if self.connection_status == 'Closed':
            print(f'{self.protocol} connection is already closed in this device.')
            return False
        self.connection.close()
        self.connection_status = 'Closed'
        self.connectivity_message = f'{self.protocol} connection closed'
        print(self.__str__())

    def get_connection_object(self):
        """
        Returns the underlying <ximu3.Connection> object if it exists.
        """
        if self.connection != None:
            return self.connection
        print("No connection to this device has been established.")
        return None
    
    def wrist_or_arm(self):
        if self.device_name == 'violet_IMU':
            return 'arm'
        if self.device_name == 'green_IMU':
            return 'wrist'
        print(f'Device name {self.device_name} not found. Must be violet_IMU or green_IMU')

    def __str__(self):
        return f"{self.device_name} {self.serial_number} ({self.connectivity_message})"
    
    def set_color(self, hex):
        return self.send_command("colour", hex)
    
    def send_command(self, key, value):
        command = f'{{"{key}":"{value}"}}' if value != 'null' else f'{{"{key}":null}}'
        try:
            response = self.connection.send_commands([command], 2, 500)[0]
            return ast.literal_eval(response)[key]
        except:
            raise Exception(f"failed to send command with key {key} and value {value}")

