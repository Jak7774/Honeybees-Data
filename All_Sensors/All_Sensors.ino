/*
   -------------------------------------------------------------------------------------
   All Sensors
   Read All Sensors from the BeeHive and send to Pi for processing
   Jack Elkes
   11NOV2023
   -------------------------------------------------------------------------------------
*/

#include <OneWire.h>
#include <DallasTemperature.h>
#include <Arduino.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"
#include <HX711_ADC.h>

#include <HX711_ADC.h>
#if defined(ESP8266)|| defined(ESP32) || defined(AVR)
#include <EEPROM.h>
#endif

/* --- Setup Temperature Sensors --- */
#define ONE_WIRE_BUS 2 // Temp pins on D2 
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

/* --- Setup Humidity Sensors ---*/
Adafruit_SHT31 sht31 = Adafruit_SHT31(); 
float temp[2]; 
float humid[2];

/* Analogue Transmission of Data */
void TCA9548A(uint8_t bus){
  Wire.beginTransmission(0x71);  // TCA9548A address is 0x70
  Wire.write(1 << bus);          // send byte to select bus
  Wire.endTransmission();
}

/* --- Setup Scale Sensors --- */
const int HX711_dout = 5; //mcu > HX711 dout pin
const int HX711_sck = 6; //mcu > HX711 sck pin

//HX711 constructor:
HX711_ADC LoadCell(HX711_dout, HX711_sck);
unsigned long t = 0;
const int calVal_eepromAdress = 0;

bool printRequest = false;

/* -----------------------------
  Setup Sensors
  -----------------------------*/

void setup(void) {
  Serial.begin(9600);
  Serial.flush();
  sensors.begin(); // temp sensors
  Wire.begin(); // I2C Multiplexer
  
  if (!sht31.begin(0x44) && !sht31.begin(0x45)) {
    Serial.println("Couldn't find SHT31");
  }

  float calibrationValue;
#if defined(ESP8266) || defined(ESP32)
  EEPROM.begin(512);
#endif
  EEPROM.get(calVal_eepromAdress, calibrationValue);

  LoadCell.begin();
  unsigned long stabilizingtime = 2000;
  boolean _tare = false;
  LoadCell.start(stabilizingtime, _tare);
  if (!LoadCell.getTareTimeoutFlag()) {
    LoadCell.setCalFactor(calibrationValue);
  }
}

/* -----------------------------
   Check if serial data is available (request from Python)
   -----------------------------*/
   
void checkSerial() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    printRequest = (command == 'P');
  }
}

/* -----------------------------
  Loop to Read Sensors and send to Serial
  -----------------------------*/

void loop(void) {
  checkSerial();
  if (printRequest) {
    sensors.requestTemperatures();
    float temp1 = sensors.getTempCByIndex(0);
    float temp2 = sensors.getTempCByIndex(1);
    
    for (int i = 0; i < 2; i++) {
      TCA9548A(i);
      temp[i] = sht31.readTemperature();
      humid[i] = sht31.readHumidity();
    }

    static boolean newDataReady = false;
    if (LoadCell.update()) newDataReady = true;
    float weight = newDataReady ? LoadCell.getData() : 0.0;
    
    Serial.print("{");
    Serial.print("\"temp1\": "); Serial.print(temp1, 2); Serial.print(", ");
    Serial.print("\"temp2\": "); Serial.print(temp2, 2); Serial.print(", ");
    Serial.print("\"humid1\": "); Serial.print(humid[0], 2); Serial.print(", ");
    Serial.print("\"temp3\": "); Serial.print(temp[0], 2); Serial.print(", ");
    Serial.print("\"humid2\": "); Serial.print(humid[1], 2); Serial.print(", ");
    Serial.print("\"temp4\": "); Serial.print(temp[1], 2); Serial.print(", ");
    Serial.print("\"weight\": "); Serial.print(weight, 2);
    Serial.println("}");
    
    printRequest = false;
  }
  delay(1);
}
