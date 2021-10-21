import picamera
from time import sleep
import face_recognition
from time import time
import os

# https://picamera.readthedocs.io/en/release-1.0/api.html


def get_number_faces():
    time_now = int(time())
    
    # take picture
    camera = picamera.PiCamera()
    # set resolution
    camera.resolution = (1024, 768)
    camera.start_preview()
    sleep(3)
    camera.capture('./camera/images/{}.jpg'.format(time_now))
    camera.stop_preview()

    # facial recognition
    image = face_recognition.load_image_file('./camera/images/{}.jpg'.format(time_now))
    face_locations = face_recognition.face_locations(image)

    # faces in picture
    num_faces = len(face_locations)

    # save picture only has faces on it
    pic_name = ''
    
    if num_faces:
        pic_name = '{0}_{1}_faces.jpg'.format(time_now, num_faces)
        os.rename('./camera/images/{}.jpg'.format(time_now), './camera/images/{}'.format(pic_name))
    else:
        os.remove('./camera/images/{}.jpg'.format(time_now))
    
    return num_faces, pic_name
        
    


    
