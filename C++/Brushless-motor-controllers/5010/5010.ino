#include <Arduino.h>
#include <SimpleFOC.h>

// NUMBER OF POLE PAIRS, NOT POLES
BLDCMotor motor = BLDCMotor(7); 
// MUST USE 6PWM FOR B-G431 DRIVER
BLDCDriver6PWM driver = BLDCDriver6PWM(PHASE_UH, PHASE_UL, PHASE_VH, PHASE_VL, PHASE_WH, PHASE_WL); 
//InlineCurrentSense currentSense = InlineCurrentSense(0.03,64.0/7.0,1,0,2);

//  Encoder(int encA, int encB , int cpr, int index)
//  - encA, encB    - encoder A and B pins
//  - ppr           - impulses per rotation  (cpr=ppr*4)
//  - index pin     - (optional input)
Encoder encoder = Encoder(ENCODER_A, ENCODER_B, 160);

// interrupt routine intialisation
void doA(){encoder.handleA();}
void doB(){encoder.handleB();}

// Which part of the buffer read from is important 
// THe ADC sasmplign intuerpt is called for both the peak and of peak meaning that 1 should have no current in it
bool toggle = false;
float volt_rest = 0;
//bool current_control = true;


// angle set point variable
float target_angle = 0;

// instantiate the commander
Commander command = Commander(Serial);
//void doTarget(char* cmd) { command.scalar(&target_angle, cmd); }
void doMotor(char* cmd){ command.motor(&motor, cmd); }

void setup() {

  // monitoring port
  Serial.begin(115200);

  Serial.println("Starting Init:");
  
  // initialise encoder hardware
  encoder.init();
  // hardware interrupt enable
  encoder.enableInterrupts(doA, doB);
    

  Serial.println("Encoder ready:");
  _delay(1000);
  
  // driver config
  // power supply voltage [V]
  driver.voltage_power_supply = 12;
  driver.init();
  Serial.println("Driver ready:");
   _delay(1000);


  // link the motor and the driver
  motor.linkDriver(&driver);
  
  // link the motor to the sensor
  motor.linkSensor(&encoder);

  // limiting motor movements
  motor.velocity_limit = 70;
  motor.voltage_limit = 1.2;
  motor.current_limit = 10;
  
  // motor phase resistance 
  //motor.phase_resistance = 0.6;
  // pwm modulation settings 
  //motor.foc_modulation = FOCModulationType::SpaceVectorPWM;
  //motor.modulation_centered = 1;
 
  // open loop control config
  motor.controller = MotionControlType::velocity_openloop;
  //motor.torque_controller = TorqueControlType::voltage; 
  //motor.controller = MotionControlType::angle;

   // set control loop type to be used
  //motor.controller = MotionControlType::torque;


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
  motor.PID_velocity.output_ramp = 10;
 
  // velocity low pass filtering time constant
  motor.LPF_velocity.Tf = 0.05;

  // angle P controller
  motor.P_angle.P = 20;

  // init motor hardware
  motor.init();
  Serial.println("Motor ready:");
  //currentSense.init(); // Current sense init has to be called after PWM start 
  motor.initFOC();
  Serial.println("FOC ready:");
  
  //motor.linkCurrentSense(&currentSense);


  // add target command T
  //command.add('T', doTarget, "target angle");   

  // subscribe motor to the commander
  command.add('M', doMotor, "motor");
    
  Serial.println("All ready:");
  Serial.println("Set the target velocity using serial terminal:");
  _delay(1000);

}

void loop() {
  // display the angle and the angular velocity to the terminal
  Serial.print("Angle ");
  Serial.print(encoder.getAngle());
  //Serial.print("\t");
  //Serial.print("Speed ");
  //Serial.println(encoder.getVelocity());

  Serial.print("Target: ");
  Serial.println(target_angle);

  // main FOC algorithm function
  // the faster you run this function the better
  // Arduino UNO loop  ~1kHz
  // Bluepill loop ~10kHz 
  motor.loopFOC();

  // Motion control function
  // velocity, position or voltage (defined in motor.controller)
  // this function can be run at much lower frequency than loopFOC() function
  // You can also use motor.move() and set the motor.target in the code
  //motor.move(target_angle);
  motor.move();

  // function intended to be used with serial plotter to monitor motor variables
  // significantly slowing the execution down!!!!
    // comment out if not needed
  motor.useMonitoring(Serial);
  motor.monitor_downsample = 0; // disable intially
  motor.monitor_variables = _MON_TARGET | _MON_VEL | _MON_ANGLE; // monitor target velocity and angle

  // user communication
  command.run();
}
