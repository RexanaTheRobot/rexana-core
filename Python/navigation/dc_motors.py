import RPi.GPIO as GPIO          
from time import sleep
import Adafruit_PCA9685
from general.util import tca_select

#enable i2c multiplexer on channel 0
tca_select(0)

#set pwm channel and frequency
pwm = Adafruit_PCA9685.PCA9685(address=0x42)
pwm.set_pwm_freq(50)

# Setup for 2 pin(no separate PWW) L298N with 2x DC motor and 5V power (3rd wheel is a free rolling caster)
# Left channels
lf_pwm = 14
lb_pwm = 15

# Right channels
rf_pwm = 13
rb_pwm = 12 

# default pwm/speed
s = 2500

def left_forward(s):
    pwm.set_pwm(lf_pwm, 0, s)

def left_backward(s):
    pwm.set_pwm(lb_pwm, 0, s)

def right_forward(s):
    pwm.set_pwm(rf_pwm, 0, s)

def right_backward(s):
    pwm.set_pwm(rb_pwm, 0, s)

def stop_all():
    pwm.set_pwm(lf_pwm, 0, 0)
    pwm.set_pwm(lb_pwm, 0, 0)
    pwm.set_pwm(rf_pwm, 0, 0)
    pwm.set_pwm(rb_pwm, 0, 0)
    

def drive_motors(lf,rf,lb,rb,time):
    stop_all()
    if lf and lb:
        print("Cant drive left engine both ways at same time")
        stop_all()
    if rf and rb:
        print("Cant drive right engine both ways at same time")
        stop_all()
    else:
        left_forward(lf)
        right_forward(rf)
        left_backward(lb)
        right_backward(rb)