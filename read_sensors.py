#-------------------------------------------------------------------------------
#
# 'Controls shed weather station
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

'''Gathers data from various sensors to capture weather conditions in shed.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import time
import datetime
import logging

# Third party modules
import rrdtool
import pigpio
import DHT22

# Application modules
import DS18B20
import settings as s
import rrd_tools


#===============================================================================
# Set up logger
#===============================================================================
log_file = 'logs/read_sensors.log'

logging.basicConfig(filename='{file_name}'.format(file_name=log_file), 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.info('--- Read Sensor Script Started ---')


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''


    #---------------------------------------------------------------------------
    # Load PIGPIO
    #---------------------------------------------------------------------------
    try:
        pi = pigpio.pi()
    except ValueError:
        print('Failed to connect to PIGPIO')
        logger.error('Failed to connect to PIGPIO ({value_error}). Exiting...'.format(
            value_error=ValueError))
        sys.exit()


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    #Set up inital values for variables
    rra_files        = []
    
    #Create RRD files if none exist
    if not os.path.exists(s.RRDTOOL_RRD_FILE):
        logger.error('RRD file not found. Exiting...')
        sys.exit()
    else:
        #Fetch data from round robin database & extract next entry time to sync loop
        logger.info('RRD file found')
        data_values = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                    '-s', str(s.UPDATE_RATE * -2))
        print(data_values)
        sensors = dict.fromkeys(data_values[1], 'U')
        print(sensors)
        next_reading  = data_values[0][1]
        logger.info('RRD FETCH: Next sensor reading at {time}'.format(
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))


    #-------------------------------------------------------------------
    # Get inside temperature and humidity
    #-------------------------------------------------------------------
    if s.SENSOR_SET['inside_temp'][s.ENABLE]:
        logger.info('Reading value from DHT22 sensor')

        #Set up sensor  
        try:
            DHT22_sensor = DHT22.sensor(pi, s.SENSOR_SET['inside_temp'][s.PIN_REF])
        except ValueError:
            print('Failed to connect to DHT22')
            logger.error('Failed to connect to DHT22 ({value_error})'.format(
                value_error=ValueError))
            logger.info('Exiting...')
            sys.exit()

        #Read sensor
        DHT22_sensor.trigger()
        time.sleep(0.2)  #Do not over poll DHT22
        sensors['inside_temp'] = DHT22_sensor.temperature()
        sensors['inside_hum']  = DHT22_sensor.humidity() 


    #-------------------------------------------------------------------
    # Check door status
    #-------------------------------------------------------------------
    if s.SENSOR_SET['door_open'][s.ENABLE]:
        logger.info('Reading value from door sensor')

        #Set up hardware
        pi.set_mode(s.SENSOR_SET['door_open'][1], pigpio.INPUT)

        #Read data
        sensors['door_open'] = pi.read(s.SENSOR_SET['door_open'][1])


    #-------------------------------------------------------------------
    # Get outside temperature
    #-------------------------------------------------------------------
    if s.SENSOR_SET['outside_temp'][s.ENABLE]:
        logger.info('Reading value from DS18B20 sensor')
        sensors['outside_temp'] = DS18B20.get_temp(s.W1_DEVICE_PATH, 
                                                   s.SENSOR_SET['outside_temp'][s.PIN_REF])
        
        #Log an error if failed to read sensor
        #Error value will exceed max on RRD file and be added as NaN
        if sensors['outside_temp'] is 999.99:
            logger.error('Failed to read DS18B20 sensor')


    #-------------------------------------------------------------------
    # Display data on screen
    #-------------------------------------------------------------------
    print(sensors)


    #-------------------------------------------------------------------
    # Add data to RRD
    #-------------------------------------------------------------------
    result = rrd_tools.update_rrd_file(s.RRDTOOL_RRD_FILE,sensors)

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
