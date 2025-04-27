import serial
import threading
from config import SERIAL_PORT, SERIAL_BAUDRATE

class SerialReader(threading.Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        self.running = True
        self.latest_data = None
        self.buffer = {}

    def run(self):
        while self.running:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if ':' in line:
                    key, val = line.split(':', 1)
                    self.buffer[key.strip()] = float(val.strip())

                # once we collected a full frame
                if all(k in self.buffer for k in ['Temperature_C', 'TDS_ppm', 'GyroX', 'GyroY', 'GyroZ', 'AccelX', 'AccelY', 'AccelZ', 'Flex Voltage']):
                    self.latest_data = {
                        "Temperature_C": self.buffer.pop('Temperature_C'),
                        "TDS_ppm": self.buffer.pop('TDS_ppm'),
                        "Flex Voltage": self.buffer.pop('Flex Voltage'), 
                        "GyroX": self.buffer.pop('GyroX'),
                        "GyroY": self.buffer.pop('GyroY'),
                        "GyroZ": self.buffer.pop('GyroZ'),
                        "AccelX": self.buffer.pop('AccelX'),
                        "AccelY": self.buffer.pop('AccelY'),
                        "AccelZ": self.buffer.pop('AccelZ'),
                    }
            except Exception as e:
                print("Serial read error:", e)

    def stop(self):
        self.running = False
        self.ser.close()

    def get_latest(self):
        return self.latest_data
