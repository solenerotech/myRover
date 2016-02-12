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

#BAsed on HC_SR04 sensor

#more info on ultrasound sensor
#http://www.modmypi.com/blog/hc-sr04-ultrasonic-range-sensor-on-the-raspberry-pi

import RPi.GPIO as GPIO
from time import sleep, time
import threading
import curses


class us_sensor_data(object):
    def __init__(self):
        self.distance = -1
        self.period = 0.1
        self.cycling = True


class us_sensor(threading.Thread):
    def __init__(self, name, trigpin, echopin, data):
        threading.Thread.__init__(self)
        self.name = name
        self.trigpin = trigpin
        self.echopin = echopin
        self.data = data
        self.cycling = True

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigpin, GPIO.OUT)
        GPIO.setup(self.echopin, GPIO.IN)
        GPIO.output(self.trigpin, False)
        sleep(1)

    def run(self):
    #this function is called by the start function, inherit from threading.thread

        sound_Speed = 343000  # [mm/s]

        print 'sensor starting...'
        while self.cycling:
            #pulse a trig
            GPIO.output(self.trigpin, True)
            sleep(0.00005)
            GPIO.output(self.trigpin, False)

            #manage a timeout in case of lost signal
            timeout = 0
            while GPIO.input(self.echopin) == 0 and self.cycling and timeout < 0.01:
                sleep(0.00001)
                timeout = timeout + 0.00001
            #if timeout>=0.1:
                #print 'lost signal'

            pulse_start = time()

            timeout = 0
            while GPIO.input(self.echopin) == 1 and self.cycling and timeout < 0.01:
                sleep(0.00001)
                timeout = timeout + 0.00001
            #if timeout>=0.1:
                #print 'lost signal'

            pulse_end = time()
            pulse_duration = pulse_end - pulse_start
            self.data.distance = round(sound_Speed * (pulse_duration / 2), 0)  # [mm]
            #note devide by 2 because the pulse_duration measures the time to go and back.
            sleep(self.data.period)

    def stop(self):
        print 'sensor stopping...'
        self.cycling = False
        sleep(0.1)
        GPIO.cleanup()
        print 'sensor stopped'


def main():
    data = us_sensor_data()
    mySensor = us_sensor('HC_SR04', 4, 17, data)
    mySensor.start()

    screen = curses.initscr()
    # turn off input echoing
    curses.noecho()
    # respond to keys immediately (don't wait for enter)
    curses.cbreak()
    # map arrow keys to special values
    screen.keypad(True)
    #timeout in millis
    screen.timeout(500)

    try:
        while mySensor.cycling:
            s = 'Distance: ' + str(mySensor.data.distance)
            screen.addstr(1, 1, 'Press any button to stop')
            screen.addstr(3, 1, s)
            #getch returns -1 if timeout
            res = screen.getch()
            if res is not -1:
                mySensor.cycling = False
    finally:
        # shut down cleanly
        curses.nocbreak()
        screen.keypad(0)
        curses.echo()
        curses.endwin()
        mySensor.stop()
    print("well done!")


if __name__ == '__main__':
    main()