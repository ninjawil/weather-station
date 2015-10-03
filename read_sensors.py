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


#===============================================================================
# Set up logger
#===============================================================================
log_directory = 'logs'
log_file = 'read_sensors.log'

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(filename='{directory}/{file_name}'.format(
                                directory=log_directory, 
                                file_name=log_file), 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.info('--- Read Sensor Script Started ---')
script_start_time = datetime.datetime.now()
logger.info('Script start time: {start_time}'.format(
    start_time=script_start_time.strftime('%Y-%m-%d %H:%M:%S'))) 


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    #Set initial variable values
    rrdtool_enable_update        = True

    #---------------------------------------------------------------------------
    # Load PIGPIO
    #---------------------------------------------------------------------------
    try:
        pi = pigpio.pi()
    except ValueError:
        print('Failed to connect to PIGPIO')
        logger.error('Failed to connect to PIGPIO ({value_error})'.format(
            value_error=ValueError))
        logger.info('Exiting...')
        sys.exit()


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    if rrdtool_enable_update:
        #Set up inital values for variables
        rra_files        = []
  
               
        #Create RRD files if none exist
        if not os.path.exists(s.RRDTOOL_RRD_FILE):
            logger.info('RRD file not found')
            logger.info('Exiting...')
            sys.exit()
        else:
            #Fetch data from round robin database & extract next entry time to sync loop
            logger.info('RRD file found')
            data_values = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                        '-s', str(s.UPDATE_RATE * -2))
            print(data_values)
            sensors = dict.fromkeys(data_values[1], 0)
            print(sensors)
            next_reading  = data_values[0][1]
            logger.info('RRD FETCH: Next sensor reading at {time}'.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))


    #-------------------------------------------------------------------
    # Get inside temperature and humidity
    #-------------------------------------------------------------------
    if s.IN_SENSOR_ENABLE:
        logger.info('Reading value from DHT22 sensor')

        #Set up sensor  
        try:
            DHT22_sensor = DHT22.sensor(pi, s.IN_SENSOR_PIN)
        except ValueError:
            print('Failed to connect to DHT22')
            logger.error('Failed to connect to DHT22 ({value_error})'.format(
                value_error=ValueError))
            logger.info('Exiting...')
            sys.exit()

        #Read sensor
        DHT22_sensor.trigger()
        time.sleep(0.2)  #Do not over poll DHT22
        sensors[s.IN_TEMP_NAME] = DHT22_sensor.temperature()
        sensors[s.IN_HUM_NAME]  = DHT22_sensor.humidity() 


    #-------------------------------------------------------------------
    # Check door status
    #-------------------------------------------------------------------
    if s.DOOR_ENABLE:
        logger.info('Reading value from door sensor')

        #Set up hardware
        pi.set_mode(s.DOOR_SENSOR_PIN, pigpio.INPUT)

        #Read data
        sensors[s.DOOR_NAME] = pi.read(s.DOOR_SENSOR_PIN)


    #-------------------------------------------------------------------
    # Get outside temperature
    #-------------------------------------------------------------------
    if s.OUT_TEMP_ENABLE:
        logger.info('Reading value from DS18B20 sensor')
        sensors[s.OUT_TEMP_NAME] = DS18B20.get_temp(s.W1_DEVICE_PATH, 
                                                    s.OUT_TEMP_SENSOR_REF)
        
        #Log an error if failed to read sensor
        #Error value will exceed max on RRD file and be added as NaN
        if sensors[s.OUT_TEMP_NAME] is 999.99:
            logger.error('Failed to read DS18B20 sensor')


    #-------------------------------------------------------------------
    # Display data on screen
    #-------------------------------------------------------------------
    print(sensors)


    #-------------------------------------------------------------------
    # Add data to RRD
    #-------------------------------------------------------------------
    if rrdtool_enable_update:
        logger.info('Updating RRD file')

        try:
            rrdtool.update(s.RRDTOOL_RRD_FILE, 
                'N:{out_temp}:{in_temp}:{in_hum}:{door}:{p_rate}:{p_accu}'.format(
                    out_temp=str(sensors[s.OUT_TEMP_NAME]),
                    in_temp=str(sensors[s.IN_TEMP_NAME]),
                    in_hum=str(sensors[s.IN_HUM_NAME]),
                    door=str(sensors[s.DOOR_NAME]),
                    p_rate='U',
                    p_accu='U'))
        except rrdtool.error:
            logger.error('Failed to update RRD file ({value_error})'.format(
                value_error=rrdtool.error))


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
