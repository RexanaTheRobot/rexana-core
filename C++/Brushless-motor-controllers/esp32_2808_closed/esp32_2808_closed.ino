/**
 * 
 * Position/angle motion control example
 * Steps:
 * 1) Configure the motor and encoder  
 * 2) Run the code
 * 3) Set the target angle (in radians) from serial terminal
 * 
 * 
 * NOTE :
 * > Arduino UNO example code for running velocity motion control using an encoder with index significantly
 * > Since Arduino UNO doesn't have enough interrupt pins we have to use software interrupt library PciManager.
 *  
 * > If running this code with Nucleo or Bluepill or any other board which has more than 2 interrupt pins 
 * > you can supply doIndex directly to the encoder.enableInterrupts(doA,doB,doIndex) and avoid using PciManger
 * 
 * > If you don't want to use index pin initialize the encoder class without index pin number:
 * > For example:
 * > - Encoder encoder = Encoder(2, 3, 8192);
 * > and initialize interrupts like this:
 * > - encoder.enableInterrupts(doA,doB)
 * 
 * Check the docs.simplefoc.com for more info about the possible encoder configuration.
 * 
 */
#include <SimpleFOC.h>
// software interrupt library
//#include <PciManager.h>


// BLDC motor & driver instance
BLDCMotor motor = BLDCMotor(7);
BLDCDriver3PWM driver = BLDCDriver3PWM(16, 13, 18, 12);

// encoder instance
Encoder encoder = Encoder(39, 36, 2048);
//Encoder encoder = Encoder(ENCODER_A, ENCODER_B, 160, ENCODER_Z);
///Encoder encoder = Encoder(ENCODER_A, ENCODER_B, 2048);

// Interrupt routine intialisation
// channel A and B callbacks
void doA(){encoder.handleA();}
void doB(){encoder.handleB();}
//void doIndex(){encoder.handleIndex();}
// If no available hadware interrupt pins use the software interrupt
//PciListenerImp listenerIndex(encoder.index_pin, doIndex);

// angle set point variable
//target variable
float target_velocity = 0;
// instantiate the commander
Commander command = Commander(Serial);
void doTarget(char* cmd) { command.scalar(&target_velocity, cmd); }

void disableMotor(char* cmd) { motor.disable(); }
void enableMotor(char* cmd) { motor.enable(); }


void setup() {
  
  // initialize encoder sensor hardware
  encoder.init();
  encoder.enableInterrupts(doA, doB); 
  // software interrupts
  //PciManager.registerListener(&listenerIndex);
  // link the motor to the sensor
  motor.linkSensor(&encoder);

  // driver config
  // power supply voltage [V]
  driver.voltage_power_supply = 12;
  driver.init();
  // link the motor and the driver
  motor.linkDriver(&driver);
  
  // aligning voltage [V]
  //motor.voltage_sensor_align = 1.2;
  motor.current_limit = 1;
  // index search velocity [rad/s]
  motor.velocity_index_search = 3;

  // set motion control loop to be used
  //motor.controller = MotionControlType::angle;
  motor.controller = MotionControlType::velocity;
  //motor.controller = MotionControlType::velocity_openloop;
  //motor.controller = MotionControlType::angle_openloop;
  motor.foc_modulation = FOCModulationType::SpaceVectorPWM;


  motor.phase_resistance = 16;
  // contoller configuration 
  // default parameters in defaults.h

  // velocity PI controller parameters
  motor.PID_velocity.P = 0.2;
  motor.PID_velocity.I = 20;
  motor.PID_velocity.D = 0;
  // default voltage_power_supply
  motor.voltage_limit = 6;
  // jerk control using voltage voltage ramp
  // default value is 300 volts per sec  ~ 0.3V per millisecond
  //motor.PID_velocity.output_ramp = 1000;
 
  // velocity low pass filtering time constant
  motor.LPF_velocity.Tf = 0.01;

  // angle P controller
  motor.P_angle.P = 20;
  //  maximal velocity of the position control
  motor.velocity_limit = 40;


  // use monitoring with serial 
  Serial.begin(115200);
  // comment out if not needed
  motor.useMonitoring(Serial);
  motor.monitor_downsample = 4; // disable intially
  motor.monitor_variables = _MON_TARGET | _MON_VEL | _MON_ANGLE; // monitor target velocity and angle
  
  // initialize motor
  motor.init();
  // align encoder and start FOC
  motor.initFOC();

  // add target command T
 command.add('T', doTarget, "target value");
  command.add('D', disableMotor, "disable");
  command.add('E', enableMotor, "enable");

  Serial.println(F("Motor ready."));
  Serial.println(F("Set the target angle using serial terminal:"));
  _delay(1000);
}

void loop() {
  // main FOC algorithm function
  // the faster you run this function the better
  // Arduino UNO loop  ~1kHz
  // Bluepill loop ~10kHz 
  motor.loopFOC();

  // Motion control function
  // velocity, position or voltage (defined in motor.controller)
  // this function can be run at much lower frequency than loopFOC() function
  // You can also use motor.move() and set the motor.target in the code
  motor.move(target_velocity);

  // function intended to be used with serial plotter to monitor motor variables
  // significantly slowing the execution down!!!!
  // motor.monitor();
  
  // user communication
  command.run();
}
