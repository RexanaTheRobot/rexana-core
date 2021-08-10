from Adafruit_GPIO import I2C
# set TCA9548A address
tca = I2C.get_i2c_device(address=0x70)

# enable extra i2c addresses
def tca_select(channel):
    """Select an individual channel."""
    if channel > 7:
        return
    tca.writeRaw8(1 << channel)