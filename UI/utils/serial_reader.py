import serial
import threading
from config import SERIAL_PORT, SERIAL_BAUDRATE
import time

class SerialReader(threading.Thread):
    def __init__(self):
        super().__init__()
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
        self.running = True
        self.latest_data = None
        self.buffer = {}
        self.in_photo_mode = False
        self.photo_data = bytearray()
        self.photo_timer = None


    def run(self):
        while self.running:
            try:
                if self.in_photo_mode:
                    # Receiving photo binary data
                    if self.ser.in_waiting:
                        chunk = self.ser.read(min(64, self.ser.in_waiting))  # Read small safe chunks
                        if b"PHOTO_END" in chunk:
                            # Found end inside chunk
                            idx = chunk.find(b"PHOTO_END")
                            photo_bytes = chunk[:idx]
                            self.photo_data.extend(photo_bytes)
                            print("[SerialReader] Photo End detected inside chunk!")

                            self._finish_photo()

                            # Process any leftover after PHOTO_END
                            rest = chunk[idx + len(b"PHOTO_END"):]
                            if rest:
                                try:
                                    lines = rest.decode('utf-8', errors='ignore').splitlines()
                                    for line in lines:
                                        self._handle_line(line)
                                except Exception as e:
                                    print("[SerialReader] Error decoding rest:", e)
                        else:
                            self.photo_data.extend(chunk)

                    # Timeout check (5 seconds)
                    if self.photo_timer and time.time() - self.photo_timer > 5:
                        print("[SerialReader] Photo receiving timeout! Cancelling photo.")
                        self._finish_photo()

                else:
                    # Normal mode: receiving text lines
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    print(f"[SerialReader] Line: {line}")
                    self._handle_line(line)

            except Exception as e:
                print("Serial read error:", e)

    def _handle_line(self, line):
        if line == "PHOTO_START":
            print("[SerialReader] Photo Start detected!")
            self.in_photo_mode = True
            self.photo_data = bytearray()
            self.photo_timer = time.time()  # Start timeout timer

        elif ':' in line:
            key, val = line.split(':', 1)
            self.buffer[key.strip()] = float(val.strip())

            if all(k in self.buffer for k in [
                'Temperature_C', 'TDS_ppm', 'GyroX', 'GyroY', 'GyroZ',
                'AccelX', 'AccelY', 'AccelZ', 'Flex Voltage'
            ]):
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




    def stop(self):
        self.running = False
        if self.ser.is_open:
            self.ser.close()

    def get_latest(self):
        return self.latest_data

    def send_command(self, command):
        try:
            self.ser.write((command + '\n').encode())
        except Exception as e:
            print("Serial send error:", e)


    def _finish_photo(self):
        self.in_photo_mode = False
        self.photo_timer = None
        if hasattr(self, 'on_photo_received') and callable(self.on_photo_received):
            self.on_photo_received(self.photo_data)
