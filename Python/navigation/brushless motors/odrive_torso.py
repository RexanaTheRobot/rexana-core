#!/usr/bin/env python3
import odrive
from odrive.enums import *
import time


# Find a connected ODrive (this will block until you connect one)
print("finding an odrive...")
odrv0 = odrive.find_any()
odrv0.axis0.requested_state = AXIS_STATE_SENSORLESS_CONTROL

print("Bus voltage is " + str(odrv0.vbus_voltage) + "V")
print("Calibration current is " + str(odrv0.axis0.motor.config.calibration_current) + "A")


def stop():
    odrv0.axis0.requested_state = 0
    odrv0.axis0.controller.input_vel = 0
    odrv0.axis0.requested_state = AXIS_STATE_IDLE

# zaxis1(3,3,1)


def zaxis1(seconds=1, speed=40, direction=1):
    odrv0.axis0.motor.config.direction = direction
    t_end = time.time() + seconds
    while time.time() < t_end:
        odrv0.axis0.controller.input_vel = speed
    else:
        odrv0.axis0.controller.input_vel = 0


def down(seconds=1.5, speed=10):
    odrv0.axis0.requested_state = AXIS_STATE_SENSORLESS_CONTROL
    t_end = time.time() + 1.1
    while time.time() < t_end:
        zaxis1(1, 5, -1)  # hack to deal with sometimes going wrong direction if not encoder
    else:
        zaxis1(seconds, speed,  -1)
        odrv0.axis0.requested_state = AXIS_STATE_IDLE


def up(seconds=2, speed=10):
    odrv0.axis0.requested_state = AXIS_STATE_SENSORLESS_CONTROL
    t_end = time.time() + 1.1
    while time.time() < t_end:
        zaxis1(1, 5, 1)  # hack to deal with sometimes going wrong direction if not encoder
    else:
        zaxis1(seconds, speed, 1)
        odrv0.axis0.requested_state = AXIS_STATE_IDLE
