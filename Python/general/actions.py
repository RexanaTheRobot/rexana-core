import json
import time
import sys
sys.path.append('/home/pi/rexana/navigation')
sys.path.append('/home/pi/rexana/arms')
from dc_motors import drive_motors, stop_all
from core_movements import *


def actionHandler(action, data):
    data = json.loads(data)
    if action == "arm_action":
        print("arm action")
        print(data["message"])
        armAction(data)
    if action == "motor_start":
        motorStart(data)
    if action == "motor_stop":
        print("\n Motor stopped")
        stop_all()
    if action == "speech":
        if data["message"]["type"] == "question":
            self.write_message({"action": "speech", "message": data["message"]['text']})
        elif data["message"]["type"] == "answer":
            self.write_message({"action": "speech", "message": data["message"]['text']})
    if message == "read_camera":
        readCamera(data)


def camLoop(self):
    """Sends camera images in an infinite loop."""
    sio = io.StringIO()
    camera.capture(sio, "jpeg", use_video_port=True)

    try:
        self.write_message(base64.b64encode(sio.getvalue()))
    except tornado.websocket.WebSocketClosedError:
        self.camera_loop.stop()


def readCamera(data):
    self.camera_loop = PeriodicCallback(self.camLoop, 10)
    self.camera_loop.start()


def armAction(data):
    eval(str((data["message"]) + '()'))


def motorStart(data):
    print("Start your engines")
    # print(data["message"])
    angle = data["message"]["angle"]
    radian = data["message"]["radian"]
    speed = data["message"]["speed"]
    print("radian " + str(radian))
    print("speed " + str(speed))

    # convert joystick "speed" to motor speed
    max_speed = 4095
    min_speed = 3000
    if speed > 1:
        s = max_speed
    else:
        s = min_speed

    if radian < 0.5:
        print('sharp right')
        drive_motors(max_speed, 0, 0, 0, 0)

    elif radian < 1:
        print('soft right')
        drive_motors(max_speed, min_speed, 0, 0, 0)

    elif radian < 2.2:
        print('straight')
        drive_motors(s, s, 0, 0, 0)

    elif radian < 2.4:
        print('soft left')
        drive_motors(min_speed, max_speed, 0, 0, 0)
    elif radian < 3:
        print('sharp left')
        drive_motors(0, max_speed, 0, 0, 0)

    elif radian < 3.6:
        print('back sharp left')
        drive_motors(0, 0, max_speed, 0, 0)

    elif radian < 4.0:
        print('back soft left')
        drive_motors(0, 0, max_speed, 30, 0)

    elif radian < 5.4:
        print('back')
        drive_motors(0, 0, s, s, 0)

    elif radian < 5.9:
        print('back soft right')
        drive_motors(0, 0, min_speed, max_speed, 0)

    elif radian < 6.3:
        print('back sharp right')
        drive_motors(0, 0, 0, max_speed, 0)
