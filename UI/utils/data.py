from config import USE_MOCK_DATA

if not USE_MOCK_DATA:
    from utils.serial_reader import SerialReader
    reader = SerialReader()
    reader.start()

import random

def generate_data():
    if USE_MOCK_DATA:
        return {
            "Temperature_C": random.uniform(2.0, 5.0),
            "TDS_ppm":       random.uniform(100, 300),
            "Flex Voltage":  random.uniform(0.5, 2.5),
            "GyroX":         random.uniform(-180, 180),
            "GyroY":         random.uniform(-180, 180),
            "GyroZ":         random.uniform(-180, 180),
            "AccelX":        random.uniform(-10, 10),
            "AccelY":        random.uniform(-10, 10),
            "AccelZ":        random.uniform(-10, 10),
        }
    else:
        data = reader.get_latest()
        if data:
            return data
        else:
            return None  # not ready yet
