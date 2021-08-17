# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
# esp.osdebug(None)
import uos
import machine
# uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
import webrepl
webrepl.start()
gc.collect()


def wifi_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(dhcp_hostname='ESP32 breadboard')
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('SSID', 'PASS')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())

wifi_connect()
