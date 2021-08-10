/** 
 * ESP32 position motion control example with encoder
 *
 */
#include <SimpleFOC.h>

// Motor instance
BLDCMotor motor = BLDCMotor(7);
//esp32 d1 vs UNO pins 
// 5 = 16*
// 10 = 5*
// 8 = 12*
// 6 = 27
// 11 = 23
// 13 = 18*

// 4 = 25
// 2 = 26
// 12 = 19
// A4 = 36*
// A5 = 39*



//BLDCDriver3PWM driver = BLDCDriver3PWM(16, 5, 18, 12);
BLDCDriver3PWM driver = BLDCDriver3PWM(16, 5, 18, 12);

// encoder instance
Encoder encoder = Encoder(39, 36, 2048);

// Interrupt routine intialisation
// channel A and B callbacks
void doA(){encoder.handleA();}
void doB(){encoder.handleB();}
//void doIndex(){encoder.handleIndex();}
// If no available hadware interrupt pins use the software interrupt
//PciListenerImp listenerIndex(encoder.index_pin, doIndex);

// angle set point variable
float target_angle = 0;
// instantiate the commander
Commander command = Commander(Serial);
void doTarget(char* cmd) { command.scalar(&target_angle, cmd); }

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
  motor.voltage_sensor_align = 3;
   
  // aligning voltage [V]
  //motor.voltage_sensor_align = 1.2;
  motor.current_limit = 3;
  // index search velocity [rad/s]
  motor.velocity_index_search = 3;

  // set motion control loop to be used
  //motor.controller = MotionControlType::angle;
  motor.controller = MotionControlType::velocity_openloop;
  //motor.controller = MotionControlType::angle_openloop;
  motor.foc_modulation = FOCModulationType::SpaceVectorPWM;

  // contoller configuration 
  // default parameters in defaults.h

  // velocity PI controller parameters
  motor.PID_velocity.P = 0.2;
  motor.PID_velocity.I = 20;
  motor.PID_velocity.D = 0;
  // default voltage_power_supply
  motor.voltage_limit = 1.2;
  // jerk control using voltage voltage ramp
  // default value is 300 volts per sec  ~ 0.3V per millisecond
  //motor.PID_velocity.output_ramp = 1000;
 
  // velocity low pass filtering time constant
  motor.LPF_velocity.Tf = 0.05;

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
  command.add('T', doTarget, "target angle");

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
  motor.move(target_angle);

  // function intended to be used with serial plotter to monitor motor variables
  // significantly slowing the execution down!!!!
  // motor.monitor();

    // display the angle and the angular velocity to the terminal
  Serial.print(encoder.getAngle());
  Serial.print("\t");
  Serial.println(encoder.getVelocity());
  
  // user communication
  command.run();
}
