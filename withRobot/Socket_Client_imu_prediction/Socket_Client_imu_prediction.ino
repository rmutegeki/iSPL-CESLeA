#include <Adafruit_BNO055.h>
#include <ESP8266WiFi.h>

const char* ssid     = "Demo";  // your network SSID (name)
const char* password = "wilco512";            // your network password

const uint16_t port = 5500;
const char* host = "192.168.137.1";
const uint16_t id = 1;

// Initialize the client library
WiFiClient client;

String buffer_string = "";


Adafruit_BNO055 bno = Adafruit_BNO055();

int count = 1;

void setup() {
  Serial.begin(115200);
  Serial.println("Orientation Sensor Test"); Serial.println("");
  /* Initialise the sensor */
  if (!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  // We start by connecting to a WiFi network
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.print("WiFi connected with IP:");  
  Serial.println(WiFi.localIP());
  Serial.print("Socket is connecting to:");  
  Serial.print(host);
  Serial.print(":");  
  Serial.println(port);
  
  if (!client.connect(host, port)) {
    Serial.println("Connection to host failed...");
    client.stop(); // Disconect Client
    return;
  }
  Serial.println("Sending Data...");
  Serial.println("Sendor ID: " + String(id));
  delay(100);
  
}

void loop()
{
  String data_string = "";

  // Just check whether the client is still connected
  if (client.connected()){
       
    //Can add VECTOR_EULER, VECTOR_MAGNETOMETER,VECTOR_GRAVITY...
    imu::Vector<3> accelerometer = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
    imu::Vector<3> gyroscope = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
    imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
    imu::Vector<3> linearacc = bno.getVector(Adafruit_BNO055::VECTOR_LINEARACCEL);
        
    data_string = String(id) + "," + 
      String(accelerometer.x()) + "," + String(accelerometer.y()) + "," + String(accelerometer.z()) + "," + 
      String(gyroscope.x()) + "," + String(gyroscope.y()) + "," + String(gyroscope.z()) + "," + 
      String(linearacc.x()) + "," + String(linearacc.y()) + "," + String(linearacc.z()) + "," + 
      String(euler.x()) + "," + String(euler.y()) + "," + String(euler.z());
  
    //Lets print the bytes used
    Serial.println(data_string + " : " + String(client.print("s" + data_string + "e;")) + " bytes");
        
    /* Set the delay between fresh samples */
    delay(11);
  } else {
    Serial.println("Client not connected");
    client.connect(host, port);
    delay(100);
    return;
  }
}
