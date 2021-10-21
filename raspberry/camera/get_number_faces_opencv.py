import picamera
from time import sleep
from time import time
import os
import numpy as np
import cv2
import imutils
import argparse
import face_recognition
from camera.check_rectangle_overlap import check_rectangle_overlap

# https://picamera.readthedocs.io/en/release-1.0/api.html


def get_number_faces():
    time_now = int(time())

    # take picture
    camera = picamera.PiCamera()
    camera.resolution = (1024, 768)
    camera.start_preview()
    sleep(3)
    camera.capture('./camera/images/{}.jpg'.format(time_now))
    camera.stop_preview()
    print('picture taken')

    # human detector with opencv
    HOGCV = cv2.HOGDescriptor()
    HOGCV.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    # read image and use the model
    image = cv2.imread('./camera/images/{}.jpg'.format(time_now))
    image = imutils.resize(image, width = min(800, image.shape[1])) 
    bounding_box_cordinates, weights =  HOGCV.detectMultiScale(image, winStride = (4, 4), padding = (8, 8))
    # change coordinates to list and recognize person if the Confidence Value is higher than 0.60
    people_count = 0
    people_coord = []
    for item in range(len(bounding_box_cordinates)):
        if weights[item][0] > 0.70:
            people_coord.append(list(bounding_box_cordinates[item]))
            people_count += 1

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # count number of faces in picture with face_recognition
    face_locations = face_recognition.face_locations(image)
    num_faces = len(face_locations)
    face_coord = [list(item) for item in face_locations]
    
    # compare opencv and face_recognition results. If face is within the rectangle from opencv substract one face since, the face belongs to the same person.
    for person in people_coord:
        for face in face_coord:
            if check_rectangle_overlap(person, face):
                num_faces -= 1
    people_from_both_libraries = people_count + num_faces

    print('opencv has recogniced {0} people and face_recognition {1} faces'.format(people_count, num_faces))
    
    # save picture only has faces on it
    pic_name = ''
    if people_from_both_libraries:
        pic_name = '{0}_{1}_people.jpg'.format(time_now, people_from_both_libraries)
        # draw retangles to compare results
        # opencv coordinates
        for person in people_coord:
            cv2.rectangle(image, (person[0], person[1]), (person[0]+person[2],person[1]+person[3]), (0,255,0), 2)
        # face_recognition coordinates
        for item in face_coord:
            cv2.rectangle(image, (item[3], item[2]), (item[1],item[0]), (0,255,0), 2)
        cv2.imwrite('./camera/images/{}'.format(pic_name), image)
        os.remove('./camera/images/{}.jpg'.format(time_now))
    else:
        os.remove('./camera/images/{}.jpg'.format(time_now))

    return people_from_both_libraries, pic_name

    

