#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>
#include <map>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>


const char* ssid = "Sadia";
const char* password = "12345678";
const char* serverURL = "http://192.168.207.199:8000/v1/api/card/employees_attendance/";
const char* serverHost = "192.168.207.199";
const int serverPort = 8000;

#define RST_PIN         D3
#define SS_PIN          D4
#define SERVO_PIN       D0
#define LCD_ADDR        0x27
#define LCD_COLS        16
#define LCD_ROWS        2

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance
Servo doorServo;
LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);

std::map<String, String> allowedStudents = {
  {"797bfb06", ": Dr. Mahfuzul"}
  //{"89f29006", ": Alina"}
};

void setup() {
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  doorServo.attach(SERVO_PIN);
  doorServo.write(0);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Welcome!");

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println("Wi-Fi Status: " + String(WiFi.status()));
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = readRFID();

    if (!uid.isEmpty()) {
      lcd.clear();
      
     

      if (isUidAllowed(uid)) {
          String studentName = allowedStudents[uid];

    
      lcd.print("Name: ");
      lcd.setCursor(4, 0);
      lcd.print(studentName); // Print student name on LCD
      lcd.setCursor(0, 1);
      lcd.print("Access granted!");
      Serial.println("Access granted!"); 
      openDoor();

        // Get current date and time
        String currentDate = "2023-05-09"; // Replace with actual date
        String currentTime = "23:12:55"; // Replace with actual time

        // Generate unique ID
        DynamicJsonDocument uniqueIdDoc(128);
        uniqueIdDoc["cur_time"] = currentTime;
        uniqueIdDoc["m_id"] = "797bfb06"; // Replace with machine's unique ID
        String uniqueId;
        serializeJson(uniqueIdDoc, uniqueId);

        sendAPIRequest(uid, currentDate, currentTime, uniqueId);
        delay(1000);
        closeDoor();
      } else {
        lcd.setCursor(0, 1);
        lcd.print("Access denied!"); // Display message on LCD
        Serial.println("Access denied!"); // Print message on serial monitor
        
      }

      delay(500);
      lcd.clear();
    }
  }
}

String readRFID() {
  String uid = "";

  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();

  return uid;
}

bool isUidAllowed(String uid) {
  return allowedStudents.find(uid) != allowedStudents.end();
}

void openDoor() {
  doorServo.write(180);
}

void closeDoor() {
  doorServo.write(0);
}

void sendAPIRequest(String rdf, String date, String checkIn, String uniqueId) {
  WiFiClient client;
  
  HTTPClient http;

  DynamicJsonDocument jsonDoc(256);
  jsonDoc["rdf"] = rdf;
  jsonDoc["date"] = date;
  jsonDoc["check_in"] = checkIn;
  if (!checkIn.isEmpty()) {
    jsonDoc["string"] = checkIn;
  }
//  if (!checkOut.isEmpty()) {
//    jsonDoc["string"] = checkOut;
//  }
  jsonDoc["797bfb06"] = uniqueId;
  String requestBody;
  serializeJson(jsonDoc, requestBody);

  Serial.println("Sending API request...");

  if (client.connect(serverHost, serverPort)) {
    http.begin(client, serverURL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "zsTqH59bu1fC7VEGop4oO2v85Lp8vu2oYT3Y6Gwh3EcfDgW5kPw85OODQauxVtP6"); // Replace with your authentication token

    int httpResponseCode = http.POST(requestBody);

    if (httpResponseCode > 0) {
      Serial.print("API response code: ");
      Serial.println(httpResponseCode);

      String responseBody = http.getString();
      Serial.println("API response body:");
      Serial.println(responseBody);

      DynamicJsonDocument responseDoc(256);
      deserializeJson(responseDoc, responseBody);

      if (httpResponseCode == 201) {
        String name = responseDoc["name"].as<String>();
        String inTime = responseDoc["in_time"].as<String>();
        String outTime = responseDoc["out_time"].as<String>();

        if (!outTime.isEmpty()) {
          Serial.println("Good Bye " + name);
          lcd.print("Good Bye " + name);
        } else {
          Serial.println("Welcome " + name);
          lcd.print("Good Bye " + name);
        }
      } else if (httpResponseCode == 200 || httpResponseCode == 400) {
        String message = responseDoc["message"].as<String>();
        Serial.println("API response message: " + message);
        lcd.print("API response message: " + message);
      } else {
        Serial.println("Unknown API response");
      }
    } else {
      Serial.print("Error sending API request. HTTP error code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
    client.stop();
  } else {
    Serial.println("Failed to connect to server");
  }
}