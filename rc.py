############################################################################
#
#    QuadcopeRPI- SW for controlling a quadcopter by RPI
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
#2015.11.05 new button key according to the standard remote controllers


import curses
import threading
from time import sleep

class rc_data(object):
    def __init__(self):
        self.cycling = True

        self.move = 'brake'
        self.speed = 40  # [%]
        self.mode = 'idle'
        self.sound = ''
        self.config = ''
        self.input = ''
        self.cycling = True


class rc(threading.Thread):

#here i can manage the remote control as a webserver or in a parallel thread
    def __init__(self,data):
        threading.Thread.__init__(self)
        self.data = data

    def run(self):
        print('rc starting...')
        while self.data.cycling:
            if self.data.input is not '':
                self.checkinput()
            sleep(0.01)

    def checkinput(self):
        if self.data.input == ord('q') or self.data.input == 'quit':
            self.data.cycling = False
        else:
            if self.data.input == 32 or self.data.input == 'brake':  # 32 =SPACEBAR
                self.data.move = 'brake'  # brake
            elif self.data.input == curses.KEY_RIGHT or self.data.input == 'right':
                self.data.move = 'right'
            elif self.data.input == curses.KEY_LEFT or self.data.input == 'left':
                self.data.move = 'left'
            elif self.data.input == curses.KEY_UP or self.data.input == 'up':
                self.data.move = 'up'
            elif self.data.input == curses.KEY_DOWN or self.data.input == 'down':
                self.data.move = 'down'
            elif self.data.input == ord('a') or self.data.input == 'acc':
                self.data.speed = 70
            elif self.data.input == ord('z') or self.data.input == 'dec':
                self.data.speed = 40
            elif self.data.input == ord('0') or self.data.input == 'idle':
                self.data.mode = 'idle'
            elif self.data.input == ord('1') or self.data.input == 'jog':
                self.data.mode = 'jog'
            elif self.data.input == ord('2') or self.data.input == 'program':
                self.data.mode = 'program'
            elif self.data.input == ord('3') or self.data.input == 'exec':
                self.data.mode = 'exec'
            elif self.data.input == ord('4') or self.data.input == 'discover':
                self.data.mode = 'discover'
            elif self.data.input == ord('5') or self.data.input == 'search':
                self.data.mode = 'search'
            elif self.data.input == ord('6') or self.data.input == '-':
                #self.data.mode = linetracking...
                pass
            elif self.data.input == ord('h') or self.data.input == 'horn':
                self.data.sound = 'horn'
            elif self.data.input == ord('y'):
                self.data.sound = 'speak 1'
            elif self.data.input == ord('u'):
                self.data.sound = 'speak 2'
            elif self.data.input == ord('i'):
                self.data.sound = 'speak 3'
            elif self.data.input == ord('o'):
                self.data.sound = 'speak 4'
            elif self.data.input == ord('p'):
                self.data.sound = 'speak 5'
            try:
                if self.data.input.startswith('speak'):
                    self.data.sound = self.data.input
            except:
                pass
            try:
                if self.data.input.startswith('config'):
                    self.data.config = self.data.input
            except:
                pass

        self.data.input = ''

    def stop(self):
        self.data.cycling = False
        print 'rc stopped'

def main():
    #not really a great test, since there is no way here to imput a data...
    my_data = rc_data()
    my_rc=rc(my_data)
    my_rc.start()
    res= raw_input()
    my_rc.data.input = ord('q')
    while my_rc.data.cycling:
        pass

    my_rc.stop()

if __name__ == '__main__':
    main()
