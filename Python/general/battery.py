import struct
import sys
import time

def batteryVolts(bus):
     address = 0x36
     read = bus.read_word_data(address, 2)
     data = struct.unpack("<H", struct.pack(">H", read))[0]
     voltage = data * 1.25 /1000/16
     return voltage

def batteryCapacity(bus):
     address = 0x36
     read = bus.read_word_data(address, 4)
     data= struct.unpack("<H", struct.pack(">H", read))[0]
     capacity = data/256
     return capacity