/*
  WiFiEsp example: WebServer

  A simple web server that shows the value of the analog input
  pins via a web page using an ESP8266 module.
  This sketch will print the IP address of your ESP8266 module (once connected)
  to the Serial monitor. From there, you can open that address in a web browser
  to display the web page.
  The web page will be automatically refreshed each 20 seconds.

  For more details see: http://yaab-arduino.blogspot.com/p/wifiesp.html
*/

#include "WiFiEsp.h"

// Emulate Serial1 on pins 6/7 if not present
#ifndef HAVE_HWSERIAL1
#include "SoftwareSerial.h"
SoftwareSerial Serial1(2, 3); // RX, TX
#endif

#define NUM_SAMPLES 10

int sum = 0;                    // sum of samples taken
float voltage = 0.0;    // calculated voltage

char ssid[] = "";            // your network SSID (name)
char pass[] = "";        // your network password
int status = WL_IDLE_STATUS;     // the Wifi radio's status
int reqCount = 0;                // number of requests received
unsigned char sample_count = 0; // current sample number
float truevoltage = 0;

int failcount = 0;
WiFiEspServer server(80);


void setup()
{
  digitalWrite(7, HIGH);
  delay(200);
  pinMode(7, OUTPUT);     
  // initialize serial for debugging
  Serial.begin(115200);
  // initialize serial for ESP module
  Serial1.begin(9600);
  // initialize ESP module
  WiFi.init(&Serial1);

  // check for the presence of the shield
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue
    while (true);
  }

  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network
    status = WiFi.begin(ssid, pass);
    failcount++;
    Serial.println("Fail count: "); 
    Serial.println(failcount);
    if (failcount > 5){
        digitalWrite(7, LOW);

    }
  }

  Serial.println("You're connected to the network");
  printWifiStatus();

  // start the web server on port 80
  server.begin();
}


void loop()
{

  // attempt to connect to WiFi network
  while ( status != WL_CONNECTED) {
    Serial.print("Attempting to connect to WPA SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network
    status = WiFi.begin(ssid, pass);

    IPAddress local_ip(192, 168, 1, 120);
    WiFi.config(local_ip);

    
    failcount++;
    Serial.println("Fail count: "); 
    Serial.println(failcount);
    if (failcount > 5){
        digitalWrite(7, LOW);

    }
  }
  // listen for incoming clients
  WiFiEspClient client = server.available();
  if (client) {
    Serial.println("New client");
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n' && currentLineIsBlank) {
          Serial.println("Sending response");
           // delay(1000);
          // send a standard http response header
          // use \r\n instead of many println statements to speedup data send
            client.print(
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Connection: close\r\n"  // the connection will be closed after completion of the response
            "\r\n");
            while (sample_count < NUM_SAMPLES) {
              sum += analogRead(A0);
              sample_count++;
              delay(10);
            }
            // calculate the voltage
            // use 5.0 for a 5.0V ADC reference voltage
            // 5.015V is the calibrated reference voltage
            voltage = ((float)sum / (float)NUM_SAMPLES * 5.13) / 1024.0;
            // send voltage for display on Serial Monitor
            // voltage multiplied by 11 when using voltage divider that
            // divides by 11. 11.132 is the calibrated voltage divide
            // value
            truevoltage = 16.05 * voltage;
        
          sample_count = 0;
          sum = 0;
          client.print(truevoltage);
          client.print("\r\n");
          break;
        }
        if (c == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        }
        else if (c != '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }
      }
    }
    // give the web browser time to receive the data
    delay(5000);

    // close the connection:
    client.stop();
    Serial.println("Client disconnected");
  }
}


void printWifiStatus()
{
  // print the SSID of the network you're attached to
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print where to go in the browser
  Serial.println();
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
  Serial.println();
}