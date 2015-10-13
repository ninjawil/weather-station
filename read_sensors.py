#-------------------------------------------------------------------------------
#
# The MIT License (MIT)
#
# Copyright (c) 2015 William De Freitas
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#-------------------------------------------------------------------------------

#!/usr/bin/env python

''' Script sets up hardware as long as sensor is enabled.

    Reads the data from the sensor and then updates the RRD file.

    Sensor value is initiated with 'U' which passed to the rrdtool will be 
    recorded as NaN. If reading sensor data fails the value is not updated and
    'U' will remain. 

    The script will not exit on sensor failure only once it finishes or if a RRD
    file is not found or PIGPIO does not load correctly.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import sys
import time
import logging
import collections

# Third party modules
import pigpio
import DHT22

# Application modules
import DS18B20
import settings as s
import rrd_tools as rrd



#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''


    #---------------------------------------------------------------------------
    # Load PIGPIO
    #---------------------------------------------------------------------------
    log_file = 'logs/read_sensors.log'

    logging.basicConfig(filename='{file_name}'.format(file_name=log_file), 
                        level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.info('--- Read Sensor Script Started ---')   
    

    #---------------------------------------------------------------------------
    # Load PIGPIO
    #---------------------------------------------------------------------------
    try:
        pi = pigpio.pi()

    except ValueError:
        logger.error('Failed to connect to PIGPIO ({value_error}). Exiting...'.format(
            value_error=ValueError))
        sys.exit()


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    try:
        next_reading  = rrd.last_update(s.RRDTOOL_RRD_FILE)
        logger.info('RRD fetch successful')
        logger.info('Next sensor reading at {time}'.format(
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))

    except ValueError:
        logger.info('RRD fetch failed. Exiting...')
        sys.exit()

    sensor_settings = collections.namedtuple('sensor_settings',
                                             'enable ref unit min max type value')

    sensor = {}
    for item in s.SENSOR_SET:
        sensor[item] = sensor_settings( s.SENSOR_SET[item][0],
                                        s.SENSOR_SET[item][1],
                                        s.SENSOR_SET[item][2],
                                        s.SENSOR_SET[item][3],
                                        s.SENSOR_SET[item][4],
                                        s.SENSOR_SET[item][5],
                                        s.SENSOR_SET[item][6])




    #-------------------------------------------------------------------
    # Get inside temperature and humidity
    #-------------------------------------------------------------------
    if sensor['inside_temp'].enable:
        logger.info('Reading value from DHT22 sensor')
  
        try:
            DHT22_sensor = DHT22.sensor(pi, sensor['inside_temp'].ref)
            DHT22_sensor.trigger()
            time.sleep(0.2)  #Do not over poll DHT22

            sensor['inside_temp'].value = DHT22_sensor.temperature()
            sensor['inside_hum'].value  = DHT22_sensor.humidity() 

        except ValueError:
            logger.error('Failed to read DHT22 ({value_error})'.format(
                value_error=ValueError))


    #-------------------------------------------------------------------
    # Check door status
    #-------------------------------------------------------------------
    if sensor['door_open'].enable:
        logger.info('Reading value from door sensor')

        try:
            pi.set_mode(sensor['door_open'].ref, pigpio.INPUT)
            sensor['door_open'].value = pi.read(sensor['door_open'].ref)

        except ValueError:
            logger.error('Failed to read door sensor ({value_error})'.format(
                value_error=ValueError))


    #-------------------------------------------------------------------
    # Get outside temperature
    #-------------------------------------------------------------------
    if sensor['outside_temp'].enable:
        logger.info('Reading value from DS18B20 sensor')

        try:
            sensor['outside_temp'].value = DS18B20.get_temp(s.W1_DEVICE_PATH, 
                                                   sensor['outside_temp'].ref)

        except ValueError:
            logger.error('Failed to read DS18B20 ({value_error})'.format(
                value_error=ValueError))
        
        #Log an error if failed to read sensor
        #Error value will exceed max on RRD file and be added as NaN
        if sensor['outside_temp'].value > 900:
            logger.error('Failed to read DS18B20 sensor (temp > 900)')


    #-------------------------------------------------------------------
    # Display data on screen
    #-------------------------------------------------------------------
    print(sensors)


    #-------------------------------------------------------------------
    # Add data to RRD
    #-------------------------------------------------------------------
    result = rrd.update_file(s.RRDTOOL_RRD_FILE, [sensor[i].value for i in sensor])

    if result == 'OK':
        logger.info('Update RRD file OK')
    else:
        logger.error('Failed to update RRD file ({value_error})'.format(
            value_error=result))


    #-------------------------------------------------------------------
    # Prepare to end script
    #-------------------------------------------------------------------
    #Stop processes
    DHT22_sensor.cancel()
    
    logger.info('--- Read Sensors Finished ---')

    sys.exit()

        

#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
