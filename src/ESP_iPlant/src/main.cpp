#include <Arduino.h>
#include <WiFi.h>
#include "DHT.h"
#include <HTTPClient.h>

/*
Simple Deep Sleep with Timer Wake Up
=====================================
ESP32 offers a deep sleep mode for effective power
saving as power is an important factor for IoT
applications. In this mode CPUs, most of the RAM,
and all the digital peripherals which are clocked
from APB_CLK are powered off. The only parts of
the chip which can still be powered on are:
RTC controller, RTC peripherals ,and RTC memories
This code displays the most basic deep sleep with
a timer to wake it up and how to store data in
RTC memory to use it over reboots
This code is under Public Domain License.
Author:
Pranav Cherukupalli <cherukupallip@gmail.com>
*/
const char* ssid = "WifiSenpai";
const char* password = "theboyz2021";

//Your Domain name with URL path or IP address with path
const char* serverName = "http://10.0.0.14:8888/add_sensor_reading";

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  10       /* Time ESP32 will go to sleep (in seconds) */

// DHT Sensor Constants

#define DHTPIN 4
#define DHTTYPE DHT11

const int Mpin = 32;
const int Lpin = 34;
const int PWR_PIN = 25;

// Light Sensor Constants

const int light_sensor_pin = 15;
int light_sensor_value = 0;

// Start DHT

DHT dht(DHTPIN, DHTTYPE);

RTC_DATA_ATTR int bootCount = 0;

/*
Set ESP32 to hibernation
*/

void hibernation() {
  // Setup the RTC Boot Counter
  ++bootCount;
  Serial.println("Boot number: " + String(bootCount));
  
  // Must setup the way the ESP32 will wake up first
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  esp_sleep_pd_config(ESP_PD_DOMAIN_MAX, ESP_PD_OPTION_OFF);
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_SLOW_MEM, ESP_PD_OPTION_OFF);
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_FAST_MEM, ESP_PD_OPTION_OFF);
  esp_deep_sleep_start();
}

void setup(){
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor

  dht.begin();

  /*
  First we configure the wake up source
  We set our ESP32 to wake up every 5 seconds
  */

  Serial.println("Setup ESP32 to send data every " + String(TIME_TO_SLEEP) +
  " Seconds");

  /*
  Now that we have setup a wake cause and if needed setup the
  peripherals state in deep sleep, we can now start going to
  deep sleep.
  In the case that no wake up sources were provided but deep
  sleep was started, it will sleep forever unless hardware
  reset occurs.
  */

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());

  pinMode(PWR_PIN,OUTPUT);
  digitalWrite(PWR_PIN,HIGH);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  float f = dht.readTemperature(true);

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  //Moisture 
  int mois = analogRead(Mpin);

  //light sensor
   int light_sensor_value = analogRead(Lpin);

    //Check WiFi connection status
    if(WiFi.status()== WL_CONNECTED){
      WiFiClient client;
      HTTPClient http;
    
      // Your Domain name with URL path or IP address with path
      http.begin(client, serverName);

      // // Specify content-type header
      // http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      // // Data to send with HTTP POST
      // String httpRequestData = "api_key=tPmAT5Ab3j7F9&sensor=BME280&value1=24.25&value2=49.54&value3=1005.14";           
      // // Send HTTP POST request
      // int httpResponseCode = http.POST(httpRequestData);
      
      // If you need an HTTP request with a content type: application/json, use the following:
      http.addHeader("Content-Type", "application/json");
      char message[1000];
      // int light_sensor_value = 1;
      // int mois = 2;
      // float t = 0.2;
      // float h = 0.3;

      sprintf(message,"{\"ds\":\"4-29-2022\",\"light_intensity\": %d,\"temperature\": %f,\"humidity\": %f,\"soil_moisture\":%d,\"ts\":\"05:02PM\"}",light_sensor_value,t,h,mois);
      int httpResponseCode = http.POST(message);

      // If you need an HTTP request with a content type: text/plain
      // http.addHeader("Content-Type", "text/plain");
      // int httpResponseCode = http.POST("Hello, World!");
     
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
        
      // Free resources
      http.end();
    }
    else {
      Serial.println("WiFi Disconnected");
    }
  Serial.print("Temperature: ");
  Serial.println(f);
  Serial.println("\nHumidity: ");
  Serial.println(h);
  Serial.println("\nSoil Moisture: ");
  Serial.println(mois);
  Serial.println("\nLight Intensity: ");
  Serial.println(light_sensor_value);
  Serial.println("Going to sleep now");
  delay(1000);
  Serial.flush(); 
  hibernation();
  Serial.println("This will never be printed");
}

void loop(){
  //This is not going to be called
}