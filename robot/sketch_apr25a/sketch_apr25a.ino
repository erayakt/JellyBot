#define CAMERA_MODEL_AI_THINKER
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>      // Required for I2C communication
#include <MPU6050.h>   // Include MPU6050 library

// Pin connected to the data line of the DS18B20
#define ONE_WIRE_BUS 13

// TDS setup (GPIO15)
#define TDS_PIN 2

// Flexible Pressure Detector Pin
#define FLEX_PIN 12

// Create a OneWire instance
OneWire oneWire(ONE_WIRE_BUS);

// Pass the OneWire reference to Dallas Temperature sensor library
DallasTemperature sensors(&oneWire);

// Create an MPU6050 instance
MPU6050 mpu;

// Variables to store gyro offsets
int16_t gyroX_offset = 0.4;
int16_t gyroY_offset = 2.6;
int16_t gyroZ_offset = -0.2;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Initializing DS18B20 sensor...");
  sensors.begin();

  // Initialize I2C communication for the MPU6050 with custom SDA and SCL pins
  Wire.begin(14, 15);  // SDA on IO13, SCL on IO14
  
  Serial.println("Initializing MPU6050...");
  mpu.initialize();  // Initialize the MPU6050 sensor

  // Check if MPU6050 is connected properly
  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed.");
  } else {
    Serial.println("MPU6050 is connected.");
  }

  Serial.println("Ready"); // Send "Ready" to indicate Arduino is ready
}

void loop() {
  
  if (Serial.available() > 0) {
    // Handle some serial input for disengaging or other actions
  }

  sensors.requestTemperatures();  // Request temperature readings
  float tempC = sensors.getTempCByIndex(0);  // Read temperature from the first sensor

  // --- TDS Reading ---
  int tdsADC = analogRead(TDS_PIN);         // Raw analog reading (0–4095 on ESP32)
  float voltage = tdsADC * (3.3 / 4095.0); // Convert to voltage
  float tdsValue = (133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5;

  // --- Flex Sensor Reading ---
  float flex = analogRead(FLEX_PIN);
  float flex_voltage = flex * (3.3 / 4095.0); // Convert flex value to voltage

  // --- MPU6050 Reading ---
  // Get raw accelerometer and gyroscope values
  int16_t ax, ay, az;
  int16_t gx, gy, gz;

  mpu.getAcceleration(&ax, &ay, &az); // Get acceleration
  mpu.getRotation(&gx, &gy, &gz);     // Get gyroscope data

  // Convert raw acceleration values to G's (assuming 2g range)
  float accelX = ax / 16384.0;
  float accelY = ay / 16384.0;
  float accelZ = az / 16384.0 - 0.91;

  // Convert raw gyroscope values to degrees per second (assuming ±250°/s range)
  float gyroX = gx / 131.0 - gyroX_offset;
  float gyroY = gy / 131.0 - gyroY_offset;
  float gyroZ = gz / 131.0 - gyroZ_offset;

  // Print the data in a comma-separated format, include a label
  Serial.print("Temperature_C:");
  Serial.println(tempC);
  Serial.print("TDS_ADC:");
  Serial.println(tdsADC);
  Serial.print("Voltage:");
  Serial.println(voltage, 2);
  Serial.print("TDS_ppm:");
  Serial.println(tdsValue, 2);
  Serial.print("Flex Value:");
  Serial.println(flex);
  Serial.print("Flex Voltage:");
  Serial.println(flex_voltage, 2);
  

  // Print MPU6050 data (acceleration and gyroscope)
  Serial.print("AccelX:");
  Serial.println(accelX, 2);
  Serial.print("AccelY:");
  Serial.println(accelY, 2);
  Serial.print("AccelZ:");
  Serial.println(accelZ, 2);
  
  
  Serial.print("GyroX:");
  Serial.println(gyroX, 2);
  Serial.print("GyroY:");
  Serial.println(gyroY, 2);
  Serial.print("GyroZ:");
  Serial.println(gyroZ, 2);

  delay(500);  // Wait 500 milliseconds between readings
}
