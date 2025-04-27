#define CAMERA_MODEL_AI_THINKER
#include <OneWire.h>
#include <DallasTemperature.h>

// Pin connected to the data line of the DS18B20
#define ONE_WIRE_BUS 14

// TDS setup (GPIO15)
#define TDS_PIN 15

// Flexible Pressure Detector Pin
#define FLEX_PIN 13

// Create a OneWire instance
OneWire oneWire(ONE_WIRE_BUS);

// Pass the OneWire reference to Dallas Temperature sensor library
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("Initializing DS18B20 sensor...");
  sensors.begin();
  Serial.println("Ready"); // Send "Ready" to indicate Arduino is ready
}

void loop() {
  
  if (Serial.available() > 0) {

    String input = Serial.readStringUntil('\n');
    input.trim()
 
    if (input == "S") {
      
      sensors.requestTemperatures();  // Request temperature readings
    
      float tempC = sensors.getTempCByIndex(0);  // Read temperature from the first sensor
    
      // --- TDS Reading ---
      int tdsADC = analogRead(TDS_PIN);         // Raw analog reading (0–4095 on ESP32)
      float voltage = tdsADC * (3.3 / 4095.0); // Convert to voltage
      float tdsValue = (133.42 * voltage * voltage * voltage - 255.86 * voltage * voltage + 857.39 * voltage) * 0.5;
      float flex = analogRead(FLEX_PIN);
      float flex_voltage = flex * (3.3 / 4095.0)
    
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
      Serial.print("Flex Voltage:")
      Serial.println(flex_voltage)
    
      delay(50);  // Wait 2 seconds between readings
    }
    if (input == "D") {
      //TO-DO
    }
  }
}
