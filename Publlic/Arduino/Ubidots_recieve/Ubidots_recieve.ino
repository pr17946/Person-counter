#include <UbiConstants.h>
#include <UbiTypes.h>
#include <UbidotsEsp32Mqtt.h>


/****************************************
 * Include Libraries
 ****************************************/
#include "UbidotsEsp32Mqtt.h"

/****************************************
 * Define Constants
 ****************************************/
const char *UBIDOTS_TOKEN = "BBFF-GKYE5U1V2Li4i9nSOWPuqRL83bsJlA";  // Put here your Ubidots TOKEN
const char *WIFI_SSID = "Pixel_8565";      // Put here your Wi-Fi SSID
const char *WIFI_PASS = "priya123";      // Put here your Wi-Fi password
const char *DEVICE_LABEL = "asdsa";   // Replace with the device label to subscribe to
const char *VARIABLE_LABEL = "entry_variable"; // Replace with your variable label to subscribe to
const char *VARIABLE_LABEL1 = "exit_variable";

Ubidots ubidots(UBIDOTS_TOKEN);

/****************************************
 * Auxiliar Functions
 ****************************************/

void callback(char *topic, byte *payload, unsigned int length)
{
  int id = 0;
 
  
  String val = "";
  for (int i = 0; i < length; i++)
  {
    if ((char)payload[i] == '.')
    {
      break;
    }
    val = val + String((char)payload[i]);
  }
  
  int count = val.toInt();
  if (String(topic) == "/v2.0/devices/asdsa/entry_variable/lv")
  {
    Serial.print("Entry Count : ");
  }
  else
  {
    Serial.print("Exit Count : ");
  }
  Serial.println(count);
  //Blinking the onboard LED
  digitalWrite(2, HIGH);
  delay(200);
  digitalWrite(2, LOW);
  delay(200);
}

/****************************************
 * Main Functions
 ****************************************/
int id = 0;
void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  ubidots.setDebug(true);  // uncomment this to make debug messages available
  ubidots.connectToWifi(WIFI_SSID, WIFI_PASS);
  ubidots.setCallback(callback);
  ubidots.setup();
  ubidots.reconnect();
  ubidots.subscribeLastValue(DEVICE_LABEL, VARIABLE_LABEL); // Insert the dataSource and Variable's Labels
  ubidots.subscribeLastValue(DEVICE_LABEL, VARIABLE_LABEL1);
}

void loop()
{
  // put your main code here, to run repeatedly:
  if (!ubidots.connected())
  {
    ubidots.reconnect();
    ubidots.subscribeLastValue(DEVICE_LABEL, VARIABLE_LABEL); // Insert the dataSource and Variable's Labels
    
    ubidots.subscribeLastValue(DEVICE_LABEL, VARIABLE_LABEL1);
  }
  ubidots.loop();
}
