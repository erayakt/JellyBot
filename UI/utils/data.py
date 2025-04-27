from config import USE_MOCK_DATA

if not USE_MOCK_DATA:
    from utils.serial_reader import SerialReader
    reader = SerialReader()
    reader.start()

import random

def generate_data():
    if USE_MOCK_DATA:
        return _generate_mock_data()
    else:
        data = reader.get_latest()
        if data:
            return data
        else:
            # Safe fallback when serial is not ready yet
            return {
                "Temperature_C": 0.0,
                "TDS_ppm": 0.0,
                "Flex Voltage": 0.0,
                "GyroX": 0.0,
                "GyroY": 0.0,
                "GyroZ": 0.0,
                "AccelX": 0.0,
                "AccelY": 0.0,
                "AccelZ": 0.0,
            }

def _generate_mock_data():
    """Simulate mock sensor data, sometimes injecting anomalies."""
    event_chance = random.random()

    if event_chance < 0.8:
        # 80% Normal calm data
        return {
            "Temperature_C": random.uniform(2.0, 5.0),
            "TDS_ppm":       random.uniform(100, 300),
            "Flex Voltage":  random.uniform(0.5, 2.5),
            "GyroX":         random.uniform(-20, 20),
            "GyroY":         random.uniform(-20, 20),
            "GyroZ":         random.uniform(-20, 20),
            "AccelX":        random.uniform(-1, 1),
            "AccelY":        random.uniform(-1, 1),
            "AccelZ":        random.uniform(-1, 1),
        }
    else:
        # 20% Random anomaly: high energy events
        return {
            "Temperature_C": random.uniform(6.0, 12.0),
            "TDS_ppm":       random.uniform(400, 1000),
            "Flex Voltage":  random.uniform(2.0, 3.3),
            "GyroX":         random.uniform(-180, 180),
            "GyroY":         random.uniform(-180, 180),
            "GyroZ":         random.uniform(-180, 180),
            "AccelX":        random.uniform(-10, 10),
            "AccelY":        random.uniform(-10, 10),
            "AccelZ":        random.uniform(-10, 10),
        }
