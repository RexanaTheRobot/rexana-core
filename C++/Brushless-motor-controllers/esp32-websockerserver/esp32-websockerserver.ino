// Import required libraries
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ODriveArduino.h>


// Credentials 

#if defined __has_include
#if __has_include ("credentials.h")
#include "credentials.h"
#else   
// if you dont have a credentials.h file you may adjust the "secret Infos" inplace. 
#define WIFI_SSID "secret Info"
#define WIFI_PASS "secret Info"
#endif
#endif

const char *ssid = WIFI_SSID;
const char *wifi_password = WIFI_PASS;
/*
 PIN | ESP32 | ODrive
  RX |    16 |  2
  TX |    17 |  1
 GND |   GND | GND
 */

#define ESP32_UART2_PIN_TX 17
#define ESP32_UART2_PIN_RX 16

// ODrive uses 115200 baud
#define BAUDRATE 115200

// Printing with stream operator
template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }


// ODrive object //HardwareSerial Serial1;
ODriveArduino odrive(Serial1);

float vel_limit = 5.0f;
float current_lim = 5.0f;


bool ledState = LOW;
const int ledPin = 2;
bool vacState = HIGH;
const int vacPin = 25;
String motorAction = "stop";

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP Web Server</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
  html {
    font-family: Arial, Helvetica, sans-serif;
    text-align: center;
  }
  h1 {
    font-size: 1.8rem;
    color: white;
  }
  h2{
    font-size: 1.5rem;
    font-weight: bold;
    color: #143642;
  }
  .topnav {
    overflow: hidden;
    background-color: #143642;
  }
  body {
    margin: 0;
  }
  .content {
    padding: 30px;
    max-width: 600px;
    margin: 0 auto;
  }
  .card {
    background-color: #F8F7F9;;
    box-shadow: 2px 2px 12px 1px rgba(140,140,140,.5);
    padding-top:10px;
    padding-bottom:20px;
  }
  .button {
    padding: 15px 50px;
    font-size: 24px;
    text-align: center;
    outline: none;
    color: #fff;
    background-color: #0f8b8d;
    border: none;
    border-radius: 5px;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
   }
   /*.button:hover {background-color: #0f8b8d}*/
   .button:active {
     background-color: #0f8b8d;
     box-shadow: 2 2px #CDCDCD;
     transform: translateY(2px);
   }
   .state {
     font-size: 1.5rem;
     color:#8c8c8c;
     font-weight: bold;
   }
  </style>
<title>ESP Web Server</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
</head>
<body>
  <div class="topnav">
    <h1>Rexana WebSocket Server (esp32)</h1>
  </div>
  <div class="content">
    <div class="card">
      <p class="state">state: <span id="state">%STATE%</span></p>
      <p><button id="minit" class="button">Init Motors</button></p>
      <p><button id="led" class="button">Toggle</button></p>
      <p><button id="stop" class="button">Stop</button></p>
      <p><button id="forward" class="button">Forward</button></p>
      <p><button id="back" class="button">Back</button></p>
      <p><button id="left" class="button">Left</button></p>
      <p><button id="right" class="button">Right</button></p>
      <p><button id="vac" class="button">Vaccum</button></p>
    </div>
  </div>
<script>
  var gateway = `ws://${window.location.hostname}/ws`;
  var websocket;
  window.addEventListener('load', onLoad);
  function initWebSocket() {
    console.log('Trying to open a WebSocket connection...');
    websocket = new WebSocket(gateway);
    websocket.onopen    = onOpen;
    websocket.onclose   = onClose;
    websocket.onmessage = onMessage; 
  }
  function onOpen(event) {
    console.log('Connection opened');
  }
  function onClose(event) {
    console.log('Connection closed');
    setTimeout(initWebSocket, 2000);
  }
  function onMessage(event) {
    console.log(event.data)
    var state;
    if (event.data == "1"){
      state = "ON";
    }
    else{
      state = "OFF";
    }
    document.getElementById('state').innerHTML = state;
  }
  function onLoad(event) {
    initWebSocket();
    initButton();
  }
  function initButton() {
    document.getElementById('minit').addEventListener('click', minit);
    document.getElementById('led').addEventListener('click', toggle);
    document.getElementById('stop').addEventListener('click', mstop);
    document.getElementById('forward').addEventListener('click', mforward);
    document.getElementById('back').addEventListener('click', mback);
    document.getElementById('right').addEventListener('click', mright);
    document.getElementById('left').addEventListener('click', mleft);
    document.getElementById('vac').addEventListener('click', vac);
  }
  
  function minit(){
    websocket.send('minit');
  }
  
  function toggle(){
    websocket.send('toggle');
  }
  
  function mstop(){
    websocket.send('mstop');
  }
  
  function mforward(){
    websocket.send('mforward');
  }
  function mback(){
    websocket.send('mback');
  }

  function mright(){
    websocket.send('mright');
  }
  
  function mleft(){
    websocket.send('mleft');
  }
  
  function vac(){
    websocket.send('vac');
  }
</script>
</body>
</html>
)rawliteral";

void motor() {
  ws.textAll(String(motorAction));
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;      
         
    if (strcmp((char*)data, "toggle") == 0) {
      ledState = !ledState;
    }

     if (strcmp((char*)data, "vac") == 0) {
      vacState = !vacState;      
    }

    motorAction = "";
    for (size_t i = 0; i < len; i++) {
      motorAction += (char) data[i];
    }
    Serial.println(motorAction);
     
    if(motorAction == "minit"){
      int requested_state;
      requested_state = ODriveArduino::AXIS_STATE_CLOSED_LOOP_CONTROL;
      odrive.run_state(0, requested_state, false); // don't wait
      odrive.run_state(1, requested_state, false); // don't wait
     
    }
    
    if(motorAction == "mstop"){
        odrive.SetVelocity(0, 0);
        odrive.SetVelocity(1, 0);
      }else if (motorAction == "mback"){
        odrive.SetVelocity(0, 1);
        odrive.SetVelocity(1, -1);
      }else if (motorAction == "mforward"){
        odrive.SetVelocity(0, -1);
        odrive.SetVelocity(1, 1);
      }else if (motorAction == "mright"){
        odrive.SetVelocity(0, -1);
        odrive.SetVelocity(1, 0);
      }else if (motorAction == "mleft"){
        odrive.SetVelocity(0, 0);
        odrive.SetVelocity(1, 1);
      }
      motor();
  }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

String processor(const String& var){
  Serial.println(var);
  if(var == "STATE"){
    if (motorAction){
      Serial.println(motorAction);
      return motorAction;
    }
    else{
      return "stop";
    }
  }

}

void setup(){
  // Serial port for debugging purposes
  Serial.begin(115200);

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  digitalWrite(vacPin, HIGH);
  pinMode(vacPin, OUTPUT);
  digitalWrite(vacPin, LOW);
  
  // Connect to Wi-Fi
  WiFi.begin(ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

  // Print ESP Local IP Address
  Serial.println(WiFi.localIP());


  // Serial to the ODrive //UART HWSerial 1 Setup
  // Note: you must also connect GND on ODrive to GND on ESP32!
  Serial1.begin(BAUDRATE, SERIAL_8N1, ESP32_UART2_PIN_TX, ESP32_UART2_PIN_RX);
  // ## You should be able to setup another serial for more motors

  
  while (!Serial) ;  // wait for Arduino Serial 0 Monitor to open
  Serial.println("Serial 0 Ready...");
  while (!Serial1) ; // wait for Arduino Serial 1 
  Serial.println("Serial 1 Ready...");
  // ## You should be able to setup another serial for more motors
  

//  ODriveArduino odrive(Serial1);
// Set current and velocity defaults
  for (int axis = 0; axis < 2; ++axis) {
    Serial1 << "w axis" << axis << ".controller.config.vel_limit " << vel_limit << '\n';
    Serial1 << "w axis" << axis << ".motor.config.current_lim " << current_lim << '\n';
  }

// Some serial out documentation
  Serial.println("Ready!");
  Serial.println("Send the character '0' or '1' to calibrate respective motor (you must do this before you can command movement)");
  Serial.println("Send the character 's' stop");
  Serial.println("Send the character 'f' forward");
  Serial.println("Send the character 'b' reverse");
  Serial.println("Send the character 'r' right");
  Serial.println("Send the character 'l' left");
  Serial.println("Send the character 'v' to read bus voltage");
  Serial.println("Send the character 'p' to read motor positions in a 10s loop");
  Serial.println("Send the character 'c'(-) or 'C'(+) to raise and lower the current_limit (+- 5)");
 

  initWebSocket();

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", index_html, processor);
  });

  // Start server
  server.begin();
}

void loop() {
  ws.cleanupClients();
  digitalWrite(ledPin, ledState);
  digitalWrite(vacPin, vacState);

  Serial.println((String)"Vac State: " + vacState);

  if (Serial.available()) {
    char c = Serial.read();
    Serial.println((String)" Serial.Read(): " + c  );
    int requested_state;
    requested_state = ODriveArduino::AXIS_STATE_CLOSED_LOOP_CONTROL;
    Serial << "Axis" << c << ": Requesting state " << requested_state << '\n';
    odrive.run_state(0, requested_state, false); // don't wait
    odrive.run_state(1, requested_state, false); // don't wait

   // Change Current incrementally
    if (c == 'C' || c == 'c'){
      float inc = 5.0f;
      if(c=='c') inc *= -1;
      current_lim += inc;
       Serial.println((String)"Current Limit: " + current_lim);
      for (int axis = 0; axis < 2; ++axis) {
        Serial1 << "w axis" << axis << ".motor.config.current_lim " << current_lim << '\n';
      }
    }
    
    if (c == 'f') {
      Serial.println("Forward");
      odrive.SetVelocity(0, -1);
      odrive.SetVelocity(1, 1);
    }

    if (c == 'b') {
      Serial.println("Back");
      odrive.SetVelocity(0, 1);
      odrive.SetVelocity(1, -1);
    }

    if (c == 'r') {
      Serial.println("Right");
      odrive.SetVelocity(0, 1);
      odrive.SetVelocity(1, 1);
    }

   if (c == 'l') {
      Serial.println("Left");
      odrive.SetVelocity(0, -1);
      odrive.SetVelocity(1, -1);
    }

   if (c == 's') {
      Serial.println("Stop");
      odrive.SetVelocity(0, 0);
      odrive.SetVelocity(1, 0);
    }

    // Read bus voltage
    if (c == 'v') {
      //odrive_serial << "r vbus_voltage\n";
      Serial1 << "r vbus_voltage\n";
      Serial << "Vbus voltage: " << odrive.readFloat() << '\n';
    }

    // print motor positions in a 10s loop
    if (c == 'p') {
      static const unsigned long duration = 10000;
      unsigned long start = millis();
      while(millis() - start < duration) {
        for (int motor = 0; motor < 2; ++motor) {
          //odrive_serial << "r axis" << motor << ".encoder.pos_estimate\n";
          Serial1 << "r axis" << motor << ".encoder.pos_estimate\n";
          Serial << odrive.readFloat() << '\t';
        }
        Serial << '\n';
      }
    }
  }
  
}
