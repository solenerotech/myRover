# -*- coding: utf-8 -*-

#interferenza PWM con camera:
    #se lancio PWM.setup() oppure PWM.setpup(delay_hw=PWM.DELAY_HW_PCM) prima di avviare lo streming ,
    #la camera non si connette
    #se lancio  PWM.setpup()oppure PWM.setpup(delay_hw=PWM.DELAY_HW_PCM) si connette ma crusha qunado chiudo il bowser
    #anche chiamando PWM.cleanup()  prima di chiudere lo fa crushare quando chiudo

#unico work aroud pssibile e' avviare PWM.setup solo dopo che ho config la camera
#resta utile uare PCM  perche cosi' non interferisco col  sensore...

import threading
import picamera
import time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
from picamera.array import PiRGBArray
import cv2
import numpy as np


class camera_data():
    #use to pass data to CamHAndler
    def __init__(self):
        self.tracking = False
        self.cycling = True
        self.HSV = (55, 0, 0, 95, 255, 255)
        self.resolution = (320,240)
        self.config = ''
        self.center = (-1, -1)
        self.image = None
        self.mask = None


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('image.mjpg') or self.path.endswith('mask.mjpg'):
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while self.data.cycling:
                try:
                    img_jpg = ''
                    if self.path.endswith('image.mjpg'):
                        img_jpg = self.data.image
                    elif self.path.endswith('mask.mjpg'):
                        img_jpg = self.data.mask
                    self.wfile.write("--jpgboundary")
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(img_jpg.tostring()))
                    self.end_headers()
                    self.wfile.write(img_jpg.tostring())
                    self.wfile.write('--jpgboundary\r\n')
                except KeyboardInterrupt:
                    break
                except Exception:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    print(exc_type, exc_obj, exc_tb.tb_lineno)
                    break


class camserver(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data
        CamHandler.data = self.data
        self.server = HTTPServer(('', 9094), CamHandler)

    def run(self):
        try:
            print "camserver starting..."
            self.server.serve_forever()
        except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self.data.cycling = False
        time.sleep(1)
        print 'camserver stopping...'
        self.server.socket.close()
        print 'camserver stopped'


class camera(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        print 'camera starting...'
        self.data = data
        self.camera = picamera.PiCamera()
        self.camera.resolution = self.data.resolution
        self.camera.framerate = 24
        self.camera.brightness = 50  # 0/100
        self.camera.contrast = 0  # -100/100
        self.camera.start_preview()
        #camera init time = 2 sec
        time.sleep(2)
        self.data = data

    def run(self):

        while self.data.cycling:
            self.configure()
            #rawCapture init inside while to reset each cycle!
            rawCapture = PiRGBArray(self.camera)
            self.camera.capture(rawCapture, format='bgr', use_video_port=True)
            image = rawCapture.array
            self.balltracking(image)

    def stop(self):
        self.data.cycling = False
        time.sleep(1)
        print 'camera stopping...'
        self.camera.close()
        print 'camera stopped'

    def balltracking(self, image):

        #place the ball to a defined distance, for ex. 200 mm from camera
        meas_distance = 200  # mm
        #and store here the pixel radius returned
        meas_radius =  37 #px

        # display the image on screen and wait for a keypress
        # define the lower and upper boundaries of the "green"
        # ball in the HSV color space, then initialize the
        # list of tracked points
        HSVLower = np.array(cv2.cv.Scalar(self.data.HSV[0], self.data.HSV[1], self.data.HSV[2]))
        HSVUpper = np.array(cv2.cv.Scalar(self.data.HSV[3], self.data.HSV[4], self.data.HSV[5]))

        #do som filtering of the images
        blurred = cv2.GaussianBlur(image, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV)
        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, HSVLower, HSVUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        self.data.center = (-1, -1)

        if self.data.tracking:
            # find contours in the mask and initialize the current
            # (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
            center = None
            cv2.putText(self.data.image, "o", (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255))
            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use
                # it to compute the minimum enclosing circle and
                # centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # only proceed if the radius meets a minimum size
                #TODO here it could be also possible to filter contours by their circularity...
                if radius >= 5:
                    # draw the circle and centroid on the frame,
                    # then update the list of tracked points
                    cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 1)
                    cv2.line(image, (int(x - 10), int(y)), (int(x + 10), int(y)), (0, 0, 255), 1)
                    cv2.line(image, (int(x), int(y - 10)), (int(x), int(y + 10)), (0, 0, 255), 1)
                    #vector for rotation ...

                    cv2.line(image, (self.data.resolution(0)/2,self.data.resolution(1)),(int(x), int(y)), (0, 255, 255), 1)

                    cv2.putText(image, "px_r: " + str(int(radius)), (5, 10), cv2.FONT_HERSHEY_SIMPLEX,
                         0.3, (0, 0, 255))

                    curr_dist = int(meas_radius/radius * meas_distance)
                    cv2.putText(image, "dist: " + str(int(curr_dist)), (5, 20), cv2.FONT_HERSHEY_SIMPLEX,
                         0.3, (0, 0, 255))
                    cv2.putText(image, "pos: x=" + str(center[0]) + " y=" + str(center[1]), (5, 30), cv2.FONT_HERSHEY_SIMPLEX,
                         0.3, (0, 0, 255))

                    self.data.center = center
        res, self.data.image = cv2.imencode('.jpeg', image)
        res, self.data.mask = cv2.imencode('.jpeg', mask)


    def configure(self):

        if self.data.config != '':
            strg = self.data.config.split(' ')
            if strg[0] == 'config':
                print 'config: ' + self.data.config
                if strg[1] == 'Hmin':
                    #this is to manage tuple
                    self.data.HSV = [int(strg[2]),self.data.HSV[1],self.data.HSV[2],self.data.HSV[3],self.data.HSV[4],self.data.HSV[5]]
                elif strg[1] == 'Smin':
                    self.data.HSV = [self.data.HSV[0],int(strg[2]),self.data.HSV[2],self.data.HSV[3],self.data.HSV[4],self.data.HSV[5]]
                elif strg[1] == 'Vmin':
                    self.data.HSV = [self.data.HSV[0],self.data.HSV[1],int(strg[2]),self.data.HSV[3],self.data.HSV[4],self.data.HSV[5]]
                elif strg[1] == 'Hmax':
                    self.data.HSV = [self.data.HSV[0],self.data.HSV[1],self.data.HSV[2],int(strg[2]),self.data.HSV[4],self.data.HSV[5]]
                elif strg[1] == 'Smax':
                    self.data.HSV = [self.data.HSV[0],self.data.HSV[1],self.data.HSV[2],self.data.HSV[3],int(strg[2]),self.data.HSV[5]]
                elif strg[1] == 'Vmax':
                    self.data.HSV = [self.data.HSV[0],self.data.HSV[1],self.data.HSV[2],self.data.HSV[3],self.data.HSV[4],int(strg[2])]
                elif strg[1] == 'Brig':
                    self.camera.brightness = int(strg[2])
                elif strg[1] == 'Contr':
                    self.camera.contrast = int(strg[2])
                self.data.config = ''


def main():
    my_data = camera_data()
    my_camera = camera(my_data)
    my_camera.start()

    my_camserver = camserver(my_data)
    my_camserver.start()
    time.sleep(1)
    my_data.tracking = True
    res = raw_input()
    my_camera.stop()
    my_camserver.stop()

if __name__ == '__main__':
    main()
