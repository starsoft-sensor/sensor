#include <WiFi.h>
#include "AsyncUDP.h"
const char* ssid = "xxxxxx";
const char* password = "xxxxxx";

AsyncUDP udp;
// WiFiServer server(80);
String header;
bool IO32 = 0;
bool IO33 = 0;

void setup() {
  Serial.begin(115200);
  pinMode(25, INPUT_PULLUP);
  pinMode(26, INPUT_PULLUP);
  digitalWrite(32, LOW);
  digitalWrite(33, LOW);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  tcpip_adapter_ip_info_t ipInfo;
  IP4_ADDR(&ipInfo.gw, 192,168,2,1);
	IP4_ADDR(&ipInfo.netmask, 255,255,255,0);
  // server.begin();
  if (udp.connect(IPAddress(133,18,23,48), 12345)) {
    Serial.println("UDP connected");
    udp.print("1234567890");
  }
}


void loop() {
  // put your main code here, to run repeatedly:
  delay(1000);

  // WiFiClient client = server.available();
  // client.stop();
  // Serial.println("Client disconnected.");
  // Serial.println("");
}
