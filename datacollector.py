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

from us_sensor import us_sensor_data
from rc import rc_data
from speaker import speaker_data
from server import server_data
from camera import camera_data


class datacollector(rc_data, us_sensor_data, speaker_data, server_data, camera_data):

    def __init__(self):
        rc_data.__init__(self)
        us_sensor_data.__init__(self)
        speaker_data.__init__(self)
        server_data.__init__(self)
        camera_data.__init__(self)

