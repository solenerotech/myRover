############################################################################
#
#    QuadcopeRPI- SW for controlling a quadcopter by RPI
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


import threading

import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
from time import sleep


#Initialize TOrnado to use 'GET' and load index.html
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('config.html')


#Code for handling the data sent from the webpage
#Manage the websocket
class WSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        pass
        #print 'connection opened...'

    def check_origin(self, origin):
        return True

    def on_message(self, message):      # receives the data from the webpage and is stored in the variable message
        WSHandler.data.input = message

    def on_close(self):
        pass
        #print 'connection closed...'


class server_data():
    def __init__(self):
        self.input =''
        self.cycling = True

class server(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        WSHandler.data = data
        self.data = data


    def run(self):
        print 'server starting...'
        application = tornado.web.Application([
  (r'/ws', WSHandler),
  (r'/', MainHandler),
  (r'/config', ConfigHandler),
  ])

        application.listen(9093)              # starts the websockets connection
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()
        sleep(1)
        print "server stopped"

def main():

    data = server_data()
    my_ws = server(data)
    my_ws.start()
    while my_ws.data.cycling:
        if my_ws.data.input != '':
            print 'message ' + my_ws.data.input
            if my_ws.data.input == 'quit':
                my_ws.data.cycling = False
    my_ws.stop()

if __name__ == '__main__':
    main()

# http:/192.168.0.10:9093  ( for index.html)
# http:/192.168.0.10:9093/config  (for config.html)





