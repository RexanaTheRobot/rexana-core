#!/usr/bin/env python3
import sys
import time
import random
import Adafruit_PCA9685
from multiprocessing import Process
sys.path.insert(0, '/home/pi/Rexana-Robot/')
from general.util import tca_select

# enable i2c multiplexer on channel 0
tca_select(1)


# set pwm channel and frequency
pwm = Adafruit_PCA9685.PCA9685(address=0x40)
#pwm = Adafruit_PCA9685.PCA9685(address=0x42)
pwm.set_pwm_freq(60)

##########
# left side

# left hand lh
lh = 0
lh_min = 230
lh_max = 590
lh_neu = 460  # default / neutral position
lh_last = lh_neu

# left wrist lw
lw = 1
lw_min = 160
lw_max = 630
lw_neu = 600
lw_last = lw_neu

# left shoulder lower
lsl = 2
lsl_min = 280
lsl_max = 610
lsl_neu = 510
lsl_last = lsl_neu

# left shoulder upper
lsu = 3
lsu_min = 150
lsu_max = 600
lsu_neu = 360
lsu_last = lsu_neu


##########
# right side

# right hand rh
rh = 15
rh_min = 120
rh_max = 400
rh_neu = 310  # default / neutral position
rh_last = rh_neu

# right wrist rw
rw = 14
rw_min = 120
rw_max = 630
rw_neu = 220
rw_last = rw_neu

# right shoulder lower
rsl = 13
rsl_min = 100
rsl_max = 350
rsl_neu = 300
rsl_last = rsl_neu

# right shoulder upper
rsu = 12
rsu_min = 120
rsu_max = 650
rsu_neu = 170
rsu_last = rsu_neu


class Limb:

    def __init__(self, channel, min_pos, max_pos, neutral, last):
        self.channel = int(channel)
        self.min = int(min_pos)
        self.max = int(max_pos)
        self.neu = int(neutral)  # default pose
        self.last = int(last)  # last known position

# left objects
lh = Limb(lh, lh_min, lh_max, lh_neu, lh_last)  # left hand
lw = Limb(lw, lw_min, lw_max, lw_neu, lw_last)  # left wrist
lsl = Limb(lsl, lsl_min, lsl_max, lsl_neu, lsl_last)  # left arm lower
lsu = Limb(lsu, lsu_min, lsu_max, lsu_neu, lsu_last)  # left arm upper

# right objects
rh = Limb(rh, rh_min, rh_max, rh_neu, rh_last)  # left hand
rw = Limb(rw, rw_min, rw_max, rw_neu, rw_last)  # left wrist
rsl = Limb(rsl, rsl_min, rsl_max, rsl_neu, rsl_last)  # left arm lower
rsu = Limb(rsu, rsu_min, rsu_max, rsu_neu, rsu_last)  # left arm upper


# set speed servo speed by adding a pause between iterating thru the range
'''
moveLimb(rh, rsu.last, 300, speed=0.01)
moveLimb(rsu, rsu.last, 220, speed=0.01)
moveLimb(rsl, rsl.last, 500, speed=0.01)
moveLimb(lsl, lsl.last, 280, speed=0.01)
'''


def moveLimb(limb, start_pos, end_pos, speed=0.01):
    print(speed)
    start = start_pos
    end = end_pos
    order = 1
    if end < limb.max:
        limb.last = end
    else:
        limb.last = limb.max
    print(limb.last)
    if start > end:
        order = -1
    move = Process(target=moveParallel, args=(limb, start, end, order, speed)).start()


def moveParallel(limb, start, end, order, speed):
    for i in range(start, end, order):
        time.sleep(speed)
        if i < limb.min:
            print("Pos too low")
        elif i > limb.max:
            print("Pos too high")
        else:
            pwm.set_pwm(limb.channel, 0, i)


def resetAll(speed=0.005):
    # left
    print("setup reset chip")
    moveLimb(lsl, lsl.last - 1, lsl.neu, speed)
    moveLimb(rsl, rsl.last - 1, rsl.neu, speed)
    moveLimb(lsu, lsu.last - 1, lsu.neu, speed)
    moveLimb(rsu, rsu.last - 1, rsu.neu, speed)
    moveLimb(lh, lh.last - 1, lh.neu, speed)
    moveLimb(rh, rh.last - 1, rh.neu, speed)
    moveLimb(lw, lw.last - 1, lw.neu, speed)
    moveLimb(rw, rw.last - 1, rw.neu, speed)


def randomTest(speed=0.02):
    resetAll()
    n = 5
    for i in range(n):
        speed = 0.002
        delay = 0.5
        moveLimb(rsu, rsu.last, random.randint(rsu.min + 1, rsu.max - 1), speed)
        time.sleep(delay)
        moveLimb(lsu, lsu.last, random.randint(lsu.min, lsu.max - 1), speed)
        time.sleep(delay)
        moveLimb(rsl, rsl.last, random.randint(rsl.min + 1, rsl.max - 1), speed)
        time.sleep(delay)
        moveLimb(lsl, lsl.last, random.randint(lsl.min + 1, lsl.max - 1), speed)
        time.sleep(delay)
        moveLimb(rh, rh.last, random.randint(rh.min + 1, rh.max - 1), speed)
        time.sleep(delay)
        moveLimb(lh, lh.last, random.randint(lh.min + 1, lh.max - 1), speed)
        time.sleep(delay)
        moveLimb(rw, rw.last, random.randint(rw.min + 1, rw.max - 1), speed)
        time.sleep(delay)
        moveLimb(lw, lw.last, random.randint(lw.min + 1, lw.max - 1), speed)
        time.sleep(1)
    resetAll()


###############
# pre set movements

def hug(speed=0.003):
    moveLimb(lsu, lsu.last, lsu.min - 1, speed)
    moveLimb(lsl, lsl.last, lsl.min - 1, speed)
    moveLimb(rsu, rsu.last, 380 - 1, speed)
    moveLimb(rsl, rsl.last, 150 - 1, speed)
    time.sleep(0.5)
    moveLimb(lsl, lsl.last, 500, speed)
    moveLimb(rsl, rsl.last, 160, speed)
    moveLimb(lsu, lsu.last, lsu.min, speed)
    moveLimb(rsu, rsu.last, 380, speed)
    moveLimb(lw, lw.last, lw.neu, speed)
    moveLimb(rw, rw.last, rw.neu, speed)
    moveLimb(lh, lh.last, lh.neu, speed)
    moveLimb(rh, rh.last, rh.neu, speed)
    time.sleep(1)
    n = 3
    for i in range(n):
        time.sleep(0.7)
        moveLimb(lh, lh.last, lh.neu, speed)
        moveLimb(rh, rh.last, rh.neu, speed)
        moveLimb(lsl, lsl.last, 450, speed)
        moveLimb(rsl, rsl.last, 300, speed)
        time.sleep(0.8)
        moveLimb(lsl, lsl.last, 550, speed)
        moveLimb(rsl, rsl.last, 200, speed)
        time.sleep(0.8)
        moveLimb(rh, rh.last, 220, speed)
        moveLimb(lh, lh.last, 380, speed)
        time.sleep(0.8)
        moveLimb(lsl, lsl.last, 500, speed)
        moveLimb(rsl, rsl.last, 300, speed)
        moveLimb(lh, lh.last, lh.neu, speed)
        moveLimb(rh, rh.last, rh.neu, speed)
    time.sleep(5)
    resetAll()


def clap(speed=0.001, loops=6):
    moveLimb(lsl, lsl.last, 520, speed)
    moveLimb(rsl, rsl.last, 280, speed)
    moveLimb(lsu, lsu.last, lsu.min, speed)
    moveLimb(rsu, rsu.last, rsu.max, speed)
    moveLimb(lw, lw.last, lw.neu, speed)
    moveLimb(rw, rw.last, rw.neu, speed)
    moveLimb(lh, lh.last, lh.neu, speed)
    moveLimb(rh, rh.last, rh.neu, speed)
    time.sleep(0.5)
    n = loops
    for i in range(n):
        time.sleep(0.4)
        moveLimb(lsl, lsl.last, 610, speed)
        moveLimb(rsl, rsl.last, 210, speed)
        moveLimb(rh, rh.last, rh.min + 10, speed)
        moveLimb(lh, lh.last, lh.max - 60, speed)
        time.sleep(0.4)
        moveLimb(lsl, lsl.last, 520, speed)
        moveLimb(rsl, rsl.last, 280, speed)
        moveLimb(rh, rh.last, rh.neu, speed)
        moveLimb(lh, lh.last, lh.neu, speed)
    time.sleep(1)
    resetAll()


def walk(speed=0.004, loops=10):
    moveLimb(lsu, lsu.last, lsu.neu, speed)
    moveLimb(rsu, rsu.last, rsu.neu, speed)
    for i in range(loops):
        time.sleep(0.8)
        moveLimb(lsu, lsu.last, 400, speed)
        moveLimb(rsu, rsu.last, 440, speed)
        time.sleep(0.8)
        moveLimb(lsu, lsu.last, 300, speed)
        moveLimb(rsu, rsu.last, 300, speed)
    time.sleep(1)
    resetAll()


def shakehands(speed=0.004, loops=2):
    moveLimb(rsu, rsu.last, 540, speed)
    time.sleep(1)
    for i in range(loops):
        time.sleep(0.5)
        moveLimb(rsu, rsu.last, 440, speed)
        time.sleep(0.5)
        moveLimb(rsu, rsu.last, 540, speed)
    time.sleep(1)
    resetAll()


def wave(speed=0.003, loops=6):
    moveLimb(lsu, lsu.last, lsu.min - 1, speed)
    moveLimb(lsl, lsl.last, lsl.min - 1, speed)
    time.sleep(0.2)
    moveLimb(lw, lw.last, 350, 0.001)
    moveLimb(lh, lh.last, 300, 0.001)
    time.sleep(0.7)
    for i in range(loops):
        time.sleep(0.4)
        moveLimb(lw, lw.last, 410, 0.001)
        moveLimb(lh, lh.last, 300, 0.001)
        time.sleep(0.4)
        moveLimb(lw, lw.last, 350, 0.001)
        moveLimb(lh, lh.last, 350, 0.001)
    time.sleep(1)
    resetAll()


def wings1(speed=0.003, loops=6):
    moveLimb(lsl, lsl.last, lsl.min + 1, speed)
    moveLimb(rsl, rsl.last, rsl.max - 1, speed)
    time.sleep(6)
    resetAll()


def wings2(speed=0.003, loops=6):
    moveLimb(lsl, lsl.last, lsl.min + 1, speed)
    moveLimb(rsl, rsl.last, rsl.max - 1, speed)
    for i in range(loops):
        time.sleep(0.4)
        moveLimb(lsl, lsl.last, lsl.min + 60, speed)
        moveLimb(rsl, rsl.last, rsl.max - 60, speed)
        time.sleep(0.4)
        moveLimb(lsl, lsl.last, lsl.min + 1, speed)
        moveLimb(rsl, rsl.last, rsl.max - 1, speed)
    time.sleep(1)
    resetAll()


def flex(speed=0.005, loops=6):
    moveLimb(lsu, lsu.last, lsu.min - 1, speed)
    moveLimb(lsl, lsl.last, lsl.min - 1, speed)
    moveLimb(rsu, rsu.last, rsu.max - 1, speed)
    moveLimb(rsl, rsl.last, rsl.max - 1, speed)
    moveLimb(lh, lh.last, lh.neu, speed)
    moveLimb(rh, rh.last, rh.neu, speed)
    moveLimb(lw, lw.last, 350, speed)
    moveLimb(rw, rw.last, 350, speed)
    time.sleep(1)
    for i in range(loops):
        time.sleep(0.8)
        moveLimb(lh, lh.last, 240, speed)
        moveLimb(rh, rh.last, 400, speed)
        time.sleep(0.8)
        moveLimb(lh, lh.last, lh.neu, speed)
        moveLimb(rh, rh.last, rh.neu, speed)
    time.sleep(6)
    resetAll()


def dance1(speed=0.004, loops=8):
    moveLimb(lsl, lsl.last, 550, speed)
    moveLimb(rsl, rsl.last, 250, speed)
    moveLimb(lsu, lsu.last, lsu.min, speed)
    moveLimb(rsu, rsu.last, rsu.max, speed)
    moveLimb(lw, lw.last, lw.neu, speed)
    moveLimb(rw, rw.last, rw.neu, speed)
    moveLimb(lh, lh.last, lh.neu, speed)
    moveLimb(rh, rh.last, 220, speed)
    time.sleep(1)
    n = loops
    for i in range(n):
        time.sleep(0.3)
        moveLimb(lsl, lsl.last, 600, 0)
        moveLimb(rsl, rsl.last, 300, 0)
        time.sleep(0.3)
        moveLimb(lsl, lsl.last, 550, 0)
        moveLimb(rsl, rsl.last, 250, 0)
    time.sleep(1)
    resetAll()


def dance2(speed=0.004, loops=8):
    moveLimb(lsl, lsl.last, 550, speed)
    moveLimb(rsl, rsl.last, 250, speed)
    moveLimb(lsu, lsu.last, 300, speed)
    moveLimb(rsu, rsu.last, 400, speed)
    moveLimb(lw, lw.last, lw.neu, speed)
    moveLimb(rw, rw.last, rw.neu, speed)
    moveLimb(lh, lh.last, lh.neu, speed)
    moveLimb(rh, rh.last, 220, speed)
    time.sleep(1)
    n = loops
    for i in range(n):
        time.sleep(0.3)
        moveLimb(lsl, lsl.last, 600, 0)
        moveLimb(rsl, rsl.last, 300, 0)
        time.sleep(0.3)
        moveLimb(lsl, lsl.last, 550, 0)
        moveLimb(rsl, rsl.last, 250, 0)
    time.sleep(1)
    resetAll()


def dance3(speed=0.004, loops=6):
    moveLimb(lsu, lsu.last, lsu.neu, speed)
    moveLimb(rsu, rsu.last, rsu.neu, speed)
    moveLimb(lh, lh.last, 240, speed)
    moveLimb(rh, rh.last, 400, speed)
    moveLimb(lw, lw.last, 350, speed)
    moveLimb(rw, rw.last, 350, speed)
    time.sleep(1)
    for i in range(loops):
        time.sleep(0.8)
        moveLimb(lsu, lsu.last, 400, speed)
        moveLimb(rsu, rsu.last, 300, speed)
        time.sleep(0.8)
        moveLimb(lsu, lsu.last, 300, speed)
        moveLimb(rsu, rsu.last, 400, speed)
    time.sleep(1)
    resetAll()

print("fix left hand faulty wiring,start on object pickup movement")
