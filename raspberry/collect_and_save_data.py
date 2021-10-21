from time import time
import os
import sys
import requests
from sensors.get_bme280_data import get_bme280_data
from camera.get_number_faces_opencv import get_number_faces
from external_info.get_aemet_data import get_aemet_data


# set working directory as file directory
os.chdir(os.path.dirname(sys.argv[0]))

# get actual time
timestamp = int(time())

# -----------------------------------------------------------
# 
#                     HOME INFORMATION
#
# -----------------------------------------------------------
# get environmental temperature, humidity and pressure
temperature, humidity, pressure = get_bme280_data()

# get number of faces in the room
people_count, pic_name = get_number_faces()

print('time: {0}\ntemperature: {1} ºC\nhumidity: {2}%\npressure: {3} hPA\nnum_people: {4}\npic_name: {5}\n'.format(timestamp,
                                                                                                          temperature,
                                                                                                          humidity,
                                                                                                          pressure,
                                                                                                          people_count,
                                                                                                          pic_name))

# create output
out = {'timestamp': timestamp,
       'temperature': temperature,
       'humidity': humidity,
       'pressure': pressure,
       'people_count': people_count}

if pic_name: out['pic_name'] = pic_name


# send home info to aws
aws_home_url = 'url_to_aws_lambda_save-home-data'
requests.post(aws_home_url, json = out)

# -----------------------------------------------------------
# 
#                   EXTERNAL INFORMATION
#
# -----------------------------------------------------------
# extract climatic information from aemet
aemet_url = 'http://www.aemet.es/es/eltiempo/prediccion/municipios/horas/tabla/madrid-id28079' # change accordingly to location
aemet_info = get_aemet_data(aemet_url)
aemet_info['timestamp'] = timestamp

# send aemet data to aws
aws_aemet_url = 'url_to_aws_lambda_save-aemet-data'
requests.post(aws_aemet_url, json = aemet_info)
