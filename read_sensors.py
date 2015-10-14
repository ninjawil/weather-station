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
import rrd_tools



#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''


    #---------------------------------------------------------------------------
    # Set up logger
    #---------------------------------------------------------------------------
    logger = log.setup('root', '/home/pi/weather/logs/read_sensors.log')

    logger.info('--- Read Sensor Script Started ---')   
    

    #---------------------------------------------------------------------------
    # Load PIGPIO
    #---------------------------------------------------------------------------
    try:
        pi = pigpio.pi()

    except ValueError:
        logger.critical('Failed to connect to PIGPIO ({error_v}). Exiting...'.format(
            error_v=ValueError))
        sys.exit()


    #---------------------------------------------------------------------------
    # Check Rrd File And Set Up Sensor Variables
    #---------------------------------------------------------------------------
    try:
        rrd = rrd_tools.rrd_file(s.RRDTOOL_RRD_FILE)

        if sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.critical('Data sources in RRD file does not match set up.')
            logger.critical(rrd.ds_list())
            logger.critical(list(s.SENSOR_SET.keys()))
            logger.critical('Exiting...')
            sys.exit()

        logger.info('RRD fetch successful')

    except ValueError:
        logger.critical('RRD fetch failed. Exiting...')
        sys.exit()



    sensor_value = {x: 'U' for x in s.SENSOR_SET}

    sensor_settings = collections.namedtuple('sensor_settings',
                                             'enable ref unit min max type')   
    
    sensor = {}
    for item in s.SENSOR_SET:
        sensor[item] = sensor_settings( s.SENSOR_SET[item][0],
                                        s.SENSOR_SET[item][1],
                                        s.SENSOR_SET[item][2],
                                        s.SENSOR_SET[item][3],
                                        s.SENSOR_SET[item][4],
                                        s.SENSOR_SET[item][5])


    #-------------------------------------------------------------------
    # Get inside temperature and humidity
    #-------------------------------------------------------------------
    if sensor['inside_temp'].enable or sensor['inside_hum'].enable: 
        try:
            DHT22_sensor = DHT22.sensor(pi, sensor['inside_temp'].ref)
            DHT22_sensor.trigger()
            time.sleep(0.2)  #Do not over poll DHT22

            if sensor['inside_temp'].enable:
                sensor_value['inside_temp'] = DHT22_sensor.temperature()

            if sensor['inside_hum'].enable: 
                sensor_value['inside_hum']  = DHT22_sensor.humidity() 

            logger.info('Reading value from DHT22 sensor... OK')

        except ValueError:
            logger.error('Failed to read DHT22 ({value_error})'.format(
                value_error=ValueError))


    #-------------------------------------------------------------------
    # Check door status
    #-------------------------------------------------------------------
    if sensor['door_open'].enable:
        try:
            pi.set_mode(sensor['door_open'].ref, pigpio.INPUT)
            sensor_value['door_open'] = pi.read(sensor['door_open'].ref)
            logger.info('Reading value from door sensor... OK')

        except ValueError:
            logger.error('Failed to read door sensor ({value_error})'.format(
                value_error=ValueError))


    #-------------------------------------------------------------------
    # Get outside temperature
    #-------------------------------------------------------------------
    if sensor['outside_temp'].enable:

        try:
            sensor_value['outside_temp'] = DS18B20.get_temp(s.W1_DEVICE_PATH, 
                                                   sensor['outside_temp'].ref)

            if sensor_value['outside_temp'] > 900:
                logger.error('Failed to read DS18B20 sensor (temp > 900)')
                sensor_value['outside_temp'] = 'U'
            else:
                logger.info('Reading value from DS18B20 sensor... OK')

        except ValueError:
            logger.error('Failed to read DS18B20 ({value_error})'.format(
                value_error=ValueError))
        


    #-------------------------------------------------------------------
    # Add data to RRD
    #-------------------------------------------------------------------
    result = rrd.update_file(sensor_value)

    if result == 'OK':
        logger.info('Update RRD file OK')
    else:
        logger.error('Failed to update RRD file ({value_error})'.format(
            value_error=result))
        logger.error(sensor_value)


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
