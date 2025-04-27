#define CAMERA_MODEL_AI_THINKER
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>      // Required for I2C communication
#include <MPU6050.h>   // Include MPU6050 library
#include "esp_camera.h"
#include <ESP32Servo.h>

// Create a Servo instance
Servo myServo;

// SG90 Servo Pin
#define SERVO_PIN 4

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


// Camera pin definitions for AI-Thinker ESP32-CAM
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22


void initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Frame size can be adjusted
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  // Init camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}





void setup() {
  Serial.begin(115200);
  delay(1000);

  initCamera();

  Serial.println("Initializing DS18B20 sensor...");
  sensors.begin();

  // Attach the servo to the correct pin
  myServo.attach(SERVO_PIN);


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
  
  if (Serial.available()) {
    // Handle some serial input for disengaging or other actions
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input == "SNAP") {
      Serial.println("SNAP command received, taking photo...");
      delay(2000);

      // Take a photo when the SNAP command is received
      camera_fb_t *fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("Camera capture failed");
        return;
      }

      // Send photo size first
      Serial.println("PHOTO_START");

      // Send the photo data over serial
      Serial.write((const uint8_t*)fb->buf, fb->len);

      Serial.println("\nPHOTO_END");

      // Return the frame buffer to free memory
      esp_camera_fb_return(fb);
    }
    // Command to turn the servo left by 15 degrees
    else if (input == "LEFT") {
      int currentAngle = myServo.read();
      int newAngle = currentAngle - 15;
      if (newAngle < 0) newAngle = 0;  // Ensure the servo doesn't rotate beyond its limits
      myServo.write(newAngle);
      Serial.print("Servo turned left to: ");
      Serial.println(newAngle);
    }

    // Command to turn the servo right by 15 degrees
    else if (input == "RIGHT") {
      int currentAngle = myServo.read();
      int newAngle = currentAngle + 15;
      if (newAngle > 180) newAngle = 180;  // Ensure the servo doesn't rotate beyond its limits
      myServo.write(newAngle);
      Serial.print("Servo turned right to: ");
      Serial.println(newAngle);
    }
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
