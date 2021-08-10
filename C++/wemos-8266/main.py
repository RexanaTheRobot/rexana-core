import socket
import machine
from machine import Pin, PWM
import uasyncio as asyncio
import utime
import json
from machine import UART

print("Starting TchiBOT Smart")

# start web server so pumps and sensors can be accessed over sockets
# HTML to send to browsers
html = """<!DOCTYPE html>
<html>
<head> <title>Rexana Web Server</title> </head>
Rexana Web Server
</html>
"""

# uart
uart = UART(0, 115200)
# pwm
leftPWM = PWM(Pin(5), freq=500, duty=0)  # d1 GPIO5
rightPWM = PWM(Pin(4), freq=500, duty=0)  # d1 GPIO4
tasks = []


def stopAll():
    print('STOP ALL')
    # task()
    uart.write('v 0 0\n'.encode('ascii'))
    uart.write('v 1 0 \n'.encode('ascii'))
    uart.write('t 0 0\n'.encode('ascii'))
    uart.write('t 1 0\n'.encode('ascii'))
    leftPWM.duty(0)
    rightPWM.duty(0)
    if tasks:
        for task in tasks:
            task.cancel()

stopAll()

async def serve(reader, writer):
    jsonresponse = False
    command = False
    request = await reader.read(256)
    # print(request.decode())
    request_str = request.decode('utf-8').strip()
    method = request_str[0:4]
    #(headers, data) = request.decode().split("\r\n\r\n")
    if 'POST' in request_str[0:4]:
        print('Post sensor data')
        jsonresponse = True
        raw_data = data
        jsondata = ujson.loads(data)

    elif 'GET' in request_str[0:4]:

        print('get')
        request = str(request)
        stop = '/?action=stop'
        left = '/?action=left'
        right = '/?action=right'
        sensors = '/?action=get-sensors'

        if stop in request:
            print("Emergency stop")
            command = "stop"
            stopAll()

        elif left in request:
            print("left wheel")
            command = "left"
            uart.write('t 1 -1\n'.encode('ascii')
            uart.write('t 0 1\n'.encode('ascii'))
            # leftPWM.duty(5)

        elif right in request:
            print("right wheel")
            command="right"
            uart.write('t 1 1\n'.encode('ascii'))
            uart.write('t 0 -1\n'.encode('ascii'))
            # rightPWM.duty(5)

        elif sensors in request:
            jsonresponse=True
            print('Get sensor data')
            file_data=open('sensor-logs.json')
            raw_data=file_data.read()
            jsondata=ujson.loads(raw_data)
            print(jsondata)

    if jsonresponse:
        print("json response")
        # print(raw_data)
        data_len=len(bytes(raw_data, "utf-8"))
        # print(data_len)
        await writer.awrite("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length:" + str(data_len) + "\r\n\r\n" + str(jsondata))

    if command:
        data_len=len(bytes(command, "utf-8"))
        await writer.awrite("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length:" + str(command) + "\r\n\r\n" + str(command))

    else:
        print("html response")
        data_len=len(bytes(html, "utf-8"))
        await writer.awrite("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length:" + str(data_len) + "\r\n\r\n" + html)

    utime.sleep(0.2)
    await writer.wait_closed()

print("start webserver")
loop=asyncio.get_event_loop()
loop.create_task(asyncio.start_server(serve, "0.0.0.0", 80))

try:
    loop.run_forever()
except KeyboardInterrupt:
    print("closing")
    loop.close()
except:
    print("crashed ?")
    machine.reset()
