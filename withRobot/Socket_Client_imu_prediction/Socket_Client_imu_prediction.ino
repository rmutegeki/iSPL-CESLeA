#include <Adafruit_BNO055.h>

#include <ESP8266WiFi.h>

const char* ssid     = "Demo";
const char* password = "wilco512";
const uint16_t port = 5500;
const char* host = "192.168.137.1";
const uint16_t id = 2;

Adafruit_BNO055 bno = Adafruit_BNO055();


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
    Serial.print("...");
    delay(500);
  }

  Serial.print("WiFi connected with IP:");
  Serial.println(WiFi.localIP());
  Serial.print("Socket is connecting to:");
  Serial.print(host);
  Serial.print(":");
  Serial.println(port);
  delay(100);
}

void loop()
{
  //Creates a Socket Client
  WiFiClient client;
  String output_string = "";

  if (!client.connect(host, port)) {
    Serial.println("Connection to host failed");
    delay (20);
    return;
  }

  //could add VECTOR_EULER, VECTOR_MAGNETOMETER,VECTOR_GRAVITY...
  imu::Vector<3> accelerometer = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  imu::Vector<3> gyroscope = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);

  output_string = String(id) + "," + String(gyroscope.x()) + "," + String(gyroscope.y()) + "," + String(gyroscope.z()) + "," + String(accelerometer.x()) + "," + String(accelerometer.y()) + "," + String(accelerometer.z()) + "," + String(euler.x()) + "," + String(euler.y()) + "," + String(euler.z());

  Serial.println(output_string);
  client.print(output_string);

  client.stop(); // Disconect Client
  /* Set the delay between fresh samples */
  delay(20);
}
