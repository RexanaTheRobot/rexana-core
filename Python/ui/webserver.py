import json
import time
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import tornado.web
import sys
sys.path.insert(0, '/home/pi/rexana/')
from general.battery import batteryCapacity
from general.actions import actionHandler
import smbus


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/main.html")


class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        self.callback = PeriodicCallback(self.get_battery, 36000)
        self.callback.start()
        self.write_message({"message": "Opened websocket!"})

    def on_message(self, message):
        jsonMsg = json.loads(message)
        print(jsonMsg)
        print('Incoming message:', jsonMsg)
        actionHandler(jsonMsg['action'], message)

    def on_close(self):
        self.callback.stop()
        print("Closed Connection")

    def get_battery(self):
        bus = smbus.SMBus(1)
        capacity = batteryCapacity(bus)
        print("Batter capacity " + str(capacity) + "%")
        if capacity > 76:
            battery = "full green"
        elif capacity > 75:
            battery = "three-quarters blue"
        elif capacity > 50:
            battery = "half blue"
        elif capacity > 30:
            battery = "quarter blue"
        elif capacity > 25:
            battery = "quarter orange"
        elif capacity < 20:
            battery = "empty red"

        self.write_message({"action": "battery", "message": battery})

application = tornado.web.Application([
    (r'/ws', WSHandler),
    (r"/", MainHandler)
])

if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()
