############################################################################
#
#    myRover- SW for controlling a rover by RPI
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

import curses
import threading
from time import sleep
from datacollector import datacollector


class display(threading.Thread):

#here i can manage the display in a parallel thread
    def __init__(self, data):
        threading.Thread.__init__(self)

        self.data = data

    def run(self):

        print('display starting...')
        sleep(3)
        self.screen = curses.initscr()
        # map arrow keys to special v1alues
        # turn off input echoing
        curses.noecho()
        # respond to keys immediately (don't wait for enter)
        curses.cbreak()
        curses.curs_set(0)
        # map arrow keys to special v1alues
        self.screen.keypad(True)
        self.screen.timeout(100)
        self.screen.clear()

        while self.data.cycling:
            curses.flushinp()
            self.screen.clear()
            self.screen.addstr(0, 0, '1-4:mode    ARROWS:move    q:quit')
            self.screen.addstr(1, 0, 'a-z:speed   h:horn         y.u.i.o.p:speach')
            self.screen.addstr(5, 0, 'mode: ' + str(self.data.mode))
            self.screen.addstr(6, 0, 'move: ' + str(self.data.move))
            self.screen.addstr(7, 0, 'sound: ' + str(self.data.sound))
            self.screen.addstr(8, 0, 'dist: ' + str(self.data.distance))
            self.screen.addstr(8, 30, 'speed: ' + str(self.data.speed))
            #getch returns -1 if timeout
            self.data.input = self.screen.getch()

    def stop(self):
        self.data.cycling = False
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
        print 'display stopped'

def main():

    from HC_SR04 import HC_SR04
    from rc import rc

    data = datacollector()

    my_sensor = HC_SR04('S1', 4, 17,data)
    my_sensor.start()

    my_rc = rc(data)
    my_rc.start()

    my_display = display(data)
    my_display.start()

    while my_display.data.cycling is True:
        sleep(0.01)

    my_display.stop()
    my_rc.stop()
    my_sensor.stop()

if __name__ == '__main__':
    main()
