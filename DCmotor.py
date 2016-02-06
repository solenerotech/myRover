############################################################################
#
#    RoveRPI- SW for controlling a rover by RPI
#
#    Copyright (C) 2014 Oscar Ferrato (solenero tech)
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

#2015.11.04
#ineriths from motor.py
#modified the pulse

#http://cdn.shopify.com/s/files/1/0358/1801/files/HbridgeDcMotor_grande.png?466

#Note: i found 2 problems using RPIO:
#1)it is necessary to use a gpio per channel to avoid bad behaviour (the pulse length seem inverted...)
#2)Avoid DMA Channel 2: it is used by the sdcard, and avoid DMA channel 0 , used by system
#3)use  delay_hw=PWM.DELAY_VIA_PCM   to avoid interference with Picamera


from RPIO import PWM
from time import sleep
import logging


class DCmotor(object):
    """Manages the currect Angular rotation W
    Implements the IO interface using the RPIO lib
    __init_(self, name,  MBack, MForw, channel1, channel2, WMin=1, WMax=100, debug=True, simulation=True):
        MBack is the GPIO pin for Motor Backward
        MForw is the GPIO pin for Motor Forward
    More info on RPIO in http://pythonhosted.org/RPIO/index.html"""


    def __init__(self, name, MBack, MForw, channel1, channel2, WMin=-100, WMax=100,Wstall=30, debug=True,
    simulation=False):
        self.logger = logging.getLogger('myR.motor')
        self.name = name
        self.powered = False
        self.simulation = simulation
        self.pin1 = MBack
        self.pin2 = MForw
        self.channel1 = channel1
        self.channel2 = channel2
        self.debug = debug
        self.WMin = WMin
        self.WMax = WMax
        self.Wstall=Wstall

        self.W = 0
        self.mass = 0.050  # [kg]

        self.PWM = PWM

    def start(self):
        "Run the procedure to init the PWM"

        if self.simulation is False:
            try:
                if not self.PWM.is_setup():
                    self.PWM.setup(pulse_incr_us=20, delay_hw=PWM.DELAY_VIA_PCM)
                    #the subcycle by default is 20 ms=20000us  so
                    #with granularity=20us, the pulse width range become 0 - 1000

                    self.PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)  # to avoid debug messages

                if not self.PWM.is_channel_initialized(self.channel1):
                    self.PWM.init_channel(self.channel1)

                if not self.PWM.is_channel_initialized(self.channel2):
                    self.PWM.init_channel(self.channel2)
                self.powered = True
                print 'motor ' + self.name + ' starting...'
                self.logger.debug('Motor %s started', self.name)

            except ImportError:
                self.logger.critical('Failed to init RPIO...')
                self.simulation = True
                self.powered = False
        else:
            print self.name + ' in simulation mode'

    def stop(self):
        "Stop PWM signal"

        self.setW(0)
        sleep(0.1)
        if self.powered:
            self.PWM.clear_channel(self.channel1)
            self.PWM.clear_channel(self.channel2)
            self.PWM.cleanup()
            self.powered = False
        print 'motor ' + self.name + ' stopped'
        self.logger.debug('Motor %s stopped', self.name)

    def setW(self, W):
        "Checks W% is between limits than sets it"

        self.W = W

        if self.W < self.WMin:
            self.W = self.WMin
        if self.W > self.WMax:
            self.W = self.WMax

        if self.W >= self.Wstall:
            PW = int(self.W * 10)
            #from % to phisical range

            if self.powered:
                self.PWM.add_channel_pulse(self.channel1, self.pin1, 0, 0)
                self.PWM.add_channel_pulse(self.channel2, self.pin2, 0, PW)
        elif self.W <= -self.Wstall:
            PW = -int(self.W * 10)

            if self.powered:
                self.PWM.add_channel_pulse(self.channel2, self.pin2, 0, 0)
                self.PWM.add_channel_pulse(self.channel1, self.pin1, 0, PW)
        else:
            if self.powered:
                self.PWM.add_channel_pulse(self.channel1, self.pin1, 0, 0)
                self.PWM.add_channel_pulse(self.channel2, self.pin2, 0, 0)


def main():
    #Example to manage 2 motors

    W = 0
    myDCmotor0 = DCmotor('m0', 18, 23, 11, 12)
    myDCmotor1 = DCmotor('m1', 24, 25, 13, 14)
    #where 18 is  GPIO18 = pin 12
    #GPIO23 = pin 16
    #GPIO24 = pin 18
    #GPIO25 = pin 22

    print('***Press ENTER to start')
    res = raw_input()
    myDCmotor0.start()
    myDCmotor1.start()
    #NOTE:the angular motor speed W can vary from -100 (min) to 100 (max)
    #the scaling to pwm is done inside motor class

    print ('increase > a | decrease > z |quit > 9')

    cycling = True
    try:
        while cycling:

            res = raw_input()
            if res == '9':
                cycling = False
            if res == 'a':
                W = W + 30
                if  W > 90:
                    W = 90
            if res == 'z':
                W = W - 30
                if W < -90:
                    W = -90

            myDCmotor0.setW(W)
            myDCmotor1.setW(W)

            print str(W)

    finally:
        # shut down cleanly
        myDCmotor0.stop()
        myDCmotor1.stop()
        print ("well done!")


if __name__ == '__main__':
    main()