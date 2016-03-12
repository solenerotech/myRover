############################################################################
#
#    RoveRPI- SW for controlling a rover by RPI
#
#    Copyright (C) 2016 Oscar Ferrato (solenero tech)
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#    Contact me at:
#    solenero.tech@gmail.com
#    solenerotech.wordpress.com
##############################################################################


#        Front
# MLeft ******* MRight
#       *******
#       *******
#       *******
#         back


import logging
from time import sleep

from rc import rc
from server import server
from DCmotor import DCmotor
from us_sensor import us_sensor
from camera import camserver, camera
from display import display
from speaker import speaker
from datacollector import datacollector


class rover(object):

    def __init__(self, name, M0b=18, M0f=23, M1b=24, M1f=25, T1=4, E1=17, simulation=False):
#GPIO: 4 17 21 22
#pin : 7 11 13 15

#GPIO: 18 23 24 25
#pin : 12 16 18 22

        self.logger = logging.getLogger('myR.rover')
        self.name = name
        self.version = 1
        self.simulation = simulation
        self.ip = '192.168.0.10'
        self.speed = 100  # [mm/s]
        self.speedMax = 1000  # [mm/s]

        self.voltage = 6  # [V]
        self.mass = 2  # [Kg]
        self.Lenght = 180  # [mm]
        self.wheelR = 32  # [mm]

        self.time360 = 2  # [sec]

        self.data = datacollector()
        self.camera = camera(self.data)
        self.camserver = camserver(self.data)
        self.sensor = us_sensor('S1', T1, E1, self.data)
        self.motorLeft = DCmotor('MLeft', M0b, M0f, 11, 12)
        self.motorRight = DCmotor('MRight', M1b, M1f, 13, 14)

        self.rc = rc(self.data)
        self.server = server(self.data)
        #self.speaker = speaker(self.data)
        #self.display init in start() in order to read the output print from other classes

    def start(self):
        "start  all motors,sensor,rc"
        self.camera.start()
        self.camserver.start()
        self.sensor.start()
        self.server.start()
        self.rc.start()

        #self.speaker.start()

        self.display = display(self.data)
        self.display.start()

    def stop(self):
        "stop all motors,sensor,rc"

        self.display.stop()
        self.rc.stop()
        self.camserver.stop()
        self.camera.stop()
        self.server.stop()
        #self.speaker.stop()
        try:
            self.motorLeft.stop()
            self.motorRight.stop()
        except:
            pass
        try:
            self.sensor.stop()
        except:
            pass

        print 'bye bye'

    def brake(self):
        self.data.move = 'brake'
        self.motorLeft.setW(0)
        self.motorRight.setW(0)

    def up(self, time=0):
        self.data.move = 'up'
        self.motorLeft.setW(self.data.speed)
        self.motorRight.setW(self.data.speed)
        if time > 0:
            sleep(time)
            self.brake()

    def right(self, time=0):
        self.data.move = 'right'
        self.motorLeft.setW(self.data.speed)
        self.motorRight.setW(0)
        if time > 0:
            sleep(time)
            self.brake()

    def left(self, time=0):
        self.data.move = 'left'
        self.motorLeft.setW(0)
        self.motorRight.setW(self.data.speed)
        if time > 0:
            sleep(time)
            self.brake()

    def down(self, time=0):
        self.data.move ='down'
        self.motorLeft.setW(-self.data.speed)
        self.motorRight.setW(-self.data.speed)
        if time > 0:
            sleep(time)
            self.brake()

    def updatemotors(self):

        if self.data.move == 'brake':
            self.brake()
        elif self.data.move =='up':
            self.up()
        elif self.data.move =='right':
            self.right()
        elif self.data.move =='left':
            self.left()
        elif self.data.move =='down':
            self.down()
        else:
            self.brake()


    def discover(self):
        self.data.speed = 40  # slow down system
        while self.data.cycling and self.data.mode == 'discover':
            self.up()
            while self.data.distance > 100 and self.data.mode == 'discover':
                sleep(0.1)
            self.brake()
            self.down(0.5)
            self.left()
            while self.data.distance < 400 and self.data.mode == 'discover':
                sleep(0.1)
        self.brake()

    def search(self):

        #2016.03.12 - under development:
        #some more tests needed to sync distances , movement time searching areas.
        self.data.tracking = True
        self.data.speed = 40  # slow down system
        res_x = self.data.resolution[0]
        while self.data.cycling and self.data.mode == 'search':
            if self.data.center[0] >= 0:
                #there is at least a target
                if self.data.center[0] <= (res_x / 5 * 2) and self.data.distance > 100:
                    #target is far enought and  on the left side
                    self.left(time=0.1)
                    #due to delay on camera, a sleep is necessary
                    sleep(0.2)
                elif self.data.center[0] >= (res_x / 5 * 3) and self.data.distance > 100:
                    self.right(time=0.1)
                    sleep(0.2)
                elif self.data.center[0] >= (res_x / 5 * 2) and self.data.center[0] <= (res_x / 5 * 3) and self.data.distance > 100:
                    #in the center zone
                    self.up(time=0.1)
                    pass
                else:
                    #target reached!
                    self.brake()
            else:
                #target not found by vision
                self.brake()
        self.data.tracking = False

    def program(self):
        pass

    def run(self):

        while self.data.cycling and self.data.mode == 'idle':
            sleep(0.01)

        #workaround: PWM.setup is called here , when camera streaming is already up
        if self.data.cycling:
            self.motorLeft.start()
            self.motorRight.start()

        while self.data.cycling:
            if self.data.mode == 'idle':
                self.brake()
                pass
            elif self.data.mode == 'jog':
                self.updatemotors()
            elif self.data.mode == 'discover':
                self.discover()
            elif self.data.mode == 'search':
                self.search()
            elif self.data.mode == 'program':
                self.program()
            sleep(0.01)

def main():

    myrover = rover('myR')
    myrover.start()
    myrover.run()
    while myrover.data.cycling:
        pass
    myrover.stop()
    print 'well done!!!'

if __name__ == '__main__':
    main()



