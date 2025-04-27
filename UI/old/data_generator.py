import random

def generate_mock_data():
    """Returns one mock sensor frame."""
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

