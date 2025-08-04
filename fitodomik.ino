#include <Wire.h>
#include <Adafruit_BME280.h>
#include <MHZ19_uart.h>
#include "RTClib.h"
#define SOIL_PIN A6
#define RELAY_PINS {7, 6, 5, 4}
#define SENSOR_READ_TIME 2000
#define AUTO_CONTROL_TIME 10000
Adafruit_BME280 bme;
MHZ19_uart mhz19;
RTC_DS3231 rtc;
struct SensorData {
  int co2;
  float temp;
  float humidity;
  float pressure;
  int soilMoisture;
} sensors;
struct ThresholdData {
  float tempMin, tempMax;
  float humidityMin, humidityMax;
  float soilMin, soilMax;
  int co2Min, co2Max;
  bool loaded;
} thresholds = {0, 0, 0, 0, 0, 0, 0, 0, false};
struct ScheduleData {
  String lampSchedule;
  String curtainSchedule;
  bool loaded;
} schedule = {"", "", false};
unsigned long lastSensorTime = 0;
unsigned long lastAutoControlTime = 0;
int relayPins[] = RELAY_PINS;
bool relayStates[] = {false, false, false, false};
String inputString = "";
int currentHour = 0;
void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH);
    relayStates[i] = false;
  }
  Wire.begin();
  if (!bme.begin(0x76)) {
    Serial.println("BME280 init failed!");
  }
  mhz19.begin(3, 2);
  mhz19.setAutoCalibration(false);
  if (!rtc.begin()) {
    Serial.println("RTC not found!");
  } else {
    if (rtc.lostPower()) {
      rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    }
    currentHour = rtc.now().hour();
  }
  inputString.reserve(150);
  delay(2000);
  Serial.println("Multi-Sensor System with Auto Control Ready");
}
void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - lastSensorTime >= SENSOR_READ_TIME) {
    lastSensorTime = currentMillis;
    readSensors();
    sendSerialData();
  }
  if (currentMillis - lastAutoControlTime >= AUTO_CONTROL_TIME) {
    lastAutoControlTime = currentMillis;
    currentHour = rtc.now().hour(); 
    autoControlRelays();
  }
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      inputString.trim();
      if (inputString.length() > 0) {
        if (inputString.indexOf('|') > 0) {
          parseScheduleData(inputString);
        } else {
          processCommand(inputString);
        }
        inputString = "";
      }
    } else {
      inputString += inChar;
    }
  }
}
void readSensors() {
  sensors.temp = bme.readTemperature();
  sensors.humidity = bme.readHumidity();
  sensors.pressure = bme.readPressure() / 100.0F;
  sensors.co2 = mhz19.getPPM();
  int rawSoil = analogRead(SOIL_PIN);
  sensors.soilMoisture = map(rawSoil, 1023, 0, 0, 100);
}
void sendSerialData() {
  Serial.print("{\"co2\":");
  Serial.print(sensors.co2);
  Serial.print(",\"temp\":");
  Serial.print(sensors.temp);
  Serial.print(",\"humidity\":");
  Serial.print(sensors.humidity);
  Serial.print(",\"pressure\":");
  Serial.print(sensors.pressure);
  Serial.print(",\"soil\":");
  Serial.print(sensors.soilMoisture);
  for (int i = 0; i < 4; i++) {
    Serial.print(",\"relay");
    Serial.print(i + 1);
    Serial.print("\":");
    Serial.print(relayStates[i] ? "true" : "false");
  }
  Serial.print(",\"time\":\"");
  if (currentHour < 10) Serial.print("0");
  Serial.print(currentHour);
  Serial.print(":00:00\"");
  DateTime now = rtc.now();
  Serial.print(",\"date\":\"");
  if (now.day() < 10) Serial.print("0");
  Serial.print(now.day());
  Serial.print(".");
  if (now.month() < 10) Serial.print("0");
  Serial.print(now.month());
  Serial.print(".");
  Serial.print(now.year());
  Serial.print("\"");
  Serial.println("}");
}
void parseScheduleData(String data) {
  int firstSeparator = data.indexOf('|');
  int secondSeparator = data.indexOf('|', firstSeparator + 1);
  if (firstSeparator > 0 && secondSeparator > firstSeparator) {
    String thresholdData = data.substring(0, firstSeparator);
    String scheduleData = data.substring(secondSeparator + 1);
    parseThresholds(thresholdData);
    parseSchedule(scheduleData);
    Serial.println("Data loaded successfully");
  }
}
void parseThresholds(String data) {
  int index = 0;
  int startPos = 0;
  for (int i = 0; i <= data.length(); i++) {
    if (i == data.length() || data[i] == ';') {
      String threshold = data.substring(startPos, i);
      int dashPos = threshold.indexOf('-');
      if (dashPos > 0) {
        float minVal = threshold.substring(0, dashPos).toFloat();
        float maxVal = threshold.substring(dashPos + 1).toFloat();
        switch (index) {
          case 0: 
            thresholds.tempMin = minVal;
            thresholds.tempMax = maxVal;
            break;
          case 1: 
            thresholds.humidityMin = minVal;
            thresholds.humidityMax = maxVal;
            break;
          case 2: 
            thresholds.soilMin = minVal;
            thresholds.soilMax = maxVal;
            break;
          case 3: 
            thresholds.co2Min = (int)minVal;
            thresholds.co2Max = (int)maxVal;
            break;
        }
      }
      index++;
      startPos = i + 1;
    }
  }
  thresholds.loaded = true;
}
void parseSchedule(String data) {
  int separatorPos = data.indexOf(';');
  if (separatorPos > 0) {
    schedule.lampSchedule = data.substring(0, separatorPos);
    schedule.curtainSchedule = data.substring(separatorPos + 1);
    schedule.loaded = true;
  }
}
void autoControlRelays() {
  if (!thresholds.loaded) return;
  if (sensors.temp > thresholds.tempMax) {
    if (!relayStates[0]) {
      setRelay(0, true);
      Serial.println("Auto: Fan ON");
    }
  } else if (sensors.temp >= thresholds.tempMin && sensors.temp <= thresholds.tempMax) {
    if (relayStates[0]) {
      setRelay(0, false);
      Serial.println("Auto: Fan OFF");
    }
  }
  if (sensors.soilMoisture < thresholds.soilMin) {
    if (!relayStates[1]) {
      setRelay(1, true);
      Serial.println("Auto: Pump ON");
    }
  } else if (sensors.soilMoisture >= thresholds.soilMin && sensors.soilMoisture <= thresholds.soilMax) {
    if (relayStates[1]) {
      setRelay(1, false);
      Serial.println("Auto: Pump OFF");
    }
  }
  if (schedule.loaded) {
    controlBySchedule();
  }
}
void controlBySchedule() {
  bool shouldCurtainsBeOn = isTimeInSchedule(schedule.curtainSchedule, currentHour);
  if (shouldCurtainsBeOn != relayStates[2]) {
    setRelay(2, shouldCurtainsBeOn);
    Serial.print("Auto: Curtains ");
    Serial.println(shouldCurtainsBeOn ? "OPEN" : "CLOSED");
  }
  bool shouldLampBeOn = isTimeInSchedule(schedule.lampSchedule, currentHour);
  if (shouldLampBeOn != relayStates[3]) {
    setRelay(3, shouldLampBeOn);
    Serial.print("Auto: Lamp ");
    Serial.println(shouldLampBeOn ? "ON" : "OFF");
  }
}
bool isTimeInSchedule(String scheduleStr, int hour) {
  if (scheduleStr == "0" || scheduleStr == "") return false;
  int startPos = 0;
  for (int i = 0; i <= scheduleStr.length(); i++) {
    if (i == scheduleStr.length() || scheduleStr[i] == ',') {
      String interval = scheduleStr.substring(startPos, i);
      int dashPos = interval.indexOf('-');
      if (dashPos > 0) {
        int startHour = interval.substring(0, dashPos).toInt();
        int endHour = interval.substring(dashPos + 1).toInt();
        if (hour >= startHour && hour <= endHour) {
          return true;
        }
      } else {
        if (interval.toInt() == hour) {
          return true;
        }
      }
      startPos = i + 1;
    }
  }
  return false;
}
void processCommand(String cmd) {
  cmd.toUpperCase();
  if (cmd == "S") {
    sendStatus();
  }
  else if (cmd == "A+") {
    setAllRelays(true);
  }
  else if (cmd == "A-") {
    setAllRelays(false);
  }
  else if (cmd.length() == 1 && cmd[0] >= '1' && cmd[0] <= '4') {
    int relay = cmd[0] - '1';
    toggleRelay(relay);
  }
}
void setRelay(int index, bool state) {
  relayStates[index] = state;
  digitalWrite(relayPins[index], state ? LOW : HIGH);
}
void toggleRelay(int index) {
  setRelay(index, !relayStates[index]);
}
void setAllRelays(bool state) {
  for (int i = 0; i < 4; i++) {
    setRelay(i, state);
  }
}
void sendStatus() {
  Serial.print("Status: ");
  for (int i = 0; i < 4; i++) {
    Serial.print("R");
    Serial.print(i + 1);
    Serial.print(relayStates[i] ? ":ON " : ":OFF ");
  }
  Serial.println();
}