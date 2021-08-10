#include <Arduino.h>
#include <SimpleFOC.h>

//  Encoder(int encA, int encB , int cpr, int index)
//  - encA, encB    - encoder A and B pins
//  - ppr           - impulses per rotation  (cpr=ppr*4)
//  - index pin     - (optional input)
Encoder encoder = Encoder(ENCODER_A, ENCODER_B, 160, ENCODER_Z);

// interrupt routine intialisation
void doA(){encoder.handleA();}
void doB(){encoder.handleB();}


// NUMBER OF POLE PAIRS, NOT POLES
BLDCMotor motor = BLDCMotor(7); 
// MUST USE 6PWM FOR B-G431 DRIVER
BLDCDriver6PWM driver = BLDCDriver6PWM(PHASE_UH, PHASE_UL, PHASE_VH, PHASE_VL, PHASE_WH, PHASE_WL); 

// include commander interface
Commander command = Commander(Serial);
void doMotor(char* cmd) { command.motor(&motor, cmd); }
void doTarget(char* cmd) { command.scalar(&motor.target, cmd); }

void setup() {

  // monitoring port
  Serial.begin(115200);
  
  // initialise encoder hardware
  encoder.init();
  // hardware interrupt enable
  encoder.enableInterrupts(doA, doB);

  Serial.println("Encoder ready");
  _delay(1000);
  
  // driver config
  // power supply voltage [V]
  driver.voltage_power_supply = 12;
  driver.init();

  // link the motor and the driver
  motor.linkDriver(&driver);

  // limiting motor movements
  motor.voltage_limit = 1.2;   // [V] 2*phase_resistance
  motor.velocity_limit = 3; // [rad/s]
 
  // control config
  //motor.controller = MotionControlType::velocity_openloop;
  motor.controller = MotionControlType::angle;
  //motor.controller = MotionControlType::angle_openloop;

 
  
  // aligning voltage [V]
  motor.voltage_sensor_align = 1.2; // default 3V
  // index search velocity
  // default 1 rad/s
  motor.velocity_index_search = 3;


  // contoller configuration 
  // default parameters in defaults.h

  // velocity PI controller parameters
  motor.PID_velocity.P = 0.2;
  motor.PID_velocity.I = 20;
  motor.PID_velocity.D = 0;
  // jerk control using voltage voltage ramp
  // default value is 300 volts per sec  ~ 0.3V per millisecond
  //motor.PID_velocity.output_ramp = 10;
 
  // velocity low pass filtering time constant
  motor.LPF_velocity.Tf = 0.01;

  // angle P controller
  motor.P_angle.P = 20;

  // init motor hardware
  motor.init();
  Serial.println("Motor ready:");
  //currentSense.init(); // Current sense init has to be called after PWM start 
  motor.initFOC();
  
  // add the motor to the commander interface
  // The letter (here 'M') you will provide to the SimpleFOCStudio 
  command.add('M',doMotor,"motor");

  // add target command T
  command.add('T', doTarget, "target");
  command.add('t', doTarget, "target");
  
  // tell the motor to use the monitoring
  motor.useMonitoring(Serial);
  motor.monitor_downsample = 0; // disable monitor at first - optional
}

void loop() {
  // display the angle and the angular velocity to the terminal
  //Serial.print("Angle ");
  //Serial.print(encoder.getAngle());
  //Serial.print("\t");
  //Serial.print("Speed ");
  //Serial.println(encoder.getVelocity());
  motor.loopFOC();
  motor.move();
  // real-time monitoring calls
  motor.monitor();
  // real-time commander calls
  command.run();
}
