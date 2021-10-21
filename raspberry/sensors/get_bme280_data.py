import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)


def get_bme280_data():
    # get data
    calibration_params = bme280.load_calibration_params(bus, address)
    data = bme280.sample(bus, address, calibration_params)
    
    # parse data
    temperature = str(round(data.temperature, 2))
    humidity = str(round(data.humidity, 2))
    pressure = str(round(data.pressure, 2))
    
    return temperature, humidity, pressure

