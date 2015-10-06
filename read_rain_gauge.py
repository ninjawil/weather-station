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

'''Gathers data from rain gauge'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import threading
import time
import datetime
import logging

# Third party modules
import rrdtool
import pigpio

# Application modules
import settings as s


#===============================================================================
# Set up logger
#===============================================================================
log_directory = 'logs'
log_file = 'read_rain_gauge.log'

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(filename='{directory}/{file_name}'.format(
                                directory=log_directory, 
                                file_name=log_file), 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.info('--- Read Rain Gauge Script Started ---')
script_start_time = datetime.datetime.now()
logger.info('Script start time: {start_time}'.format(
    start_time=script_start_time.strftime('%Y-%m-%d %H:%M:%S'))) 


#===============================================================================
# LOAD DRIVERS
#===============================================================================
try:
    pi = pigpio.pi()
except ValueError:
    print('Failed to connect to PIGPIO')
    logger.error('Failed to connect to PIGPIO ({value_error})'.format(
        value_error=ValueError))
    logger.info('Exiting...')
    sys.exit()


#===============================================================================
# GLOBAL VARIABLES
#===============================================================================
rain_thread_next_call    = time.time()
last_rising_edge = None


#===============================================================================
# EDGE CALLBACK FUNCTION TO COUNT RAIN TICKS
#===============================================================================
def count_rain_ticks(gpio, level, tick):
    
    '''Count the ticks from a reed switch'''
    
    global precip_tick_count
    global last_rising_edge
    
    pulse = False
    
    if last_rising_edge is not None:
        #check tick in microseconds
        if pigpio.tickDiff(last_rising_edge, tick) > s.DEBOUNCE_MICROS * 1000000:
            pulse = True

    else:
        pulse = True

    if pulse:
        last_rising_edge = tick  
        precip_tick_count += 1
        logger.info('Rain tick pulse = {tick_count}'.format(tick_count=precip_tick_count))

 

#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    global precip_tick_count
    global precip_accu
    global rain_thread_next_call

    #Set initial variable values
    rrdtool_enable_update        = True
    
    rrd_data_sources             = []
    rrd_set                      = []

   
    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
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
        sensors = dict.fromkeys(data_values[1], 'U')
        print(sensors)
        next_reading  = data_values[0][1]
        logger.info('RRD FETCH: Next sensor reading at {time}'.format(
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))


    #---------------------------------------------------------------------------
    # SET UP RAIN SENSOR
    #---------------------------------------------------------------------------
    if s.SENSOR_SET['precip_acc'][ENABLE]:
        #Set up inital values for variables
        precip_tick_count = 0
        precip_accu       = 0
        last_data_values  = []
        
        #Set up rain gauge hardware
        pi.set_mode(s.SENSOR_SET['precip_acc'][PIN_REF], pigpio.INPUT)
        rain_gauge = pi.callback(s.SENSOR_SET['precip_acc'][PIN_REF], 
                                    pigpio.FALLING_EDGE, 
                                    count_rain_ticks)


    #---------------------------------------------------------------------------
    # TIMED LOOP
    #---------------------------------------------------------------------------
    try:
        while True:
            

            #-------------------------------------------------------------------
            # Delay to give update rate
            #-------------------------------------------------------------------
            sleep_length = next_reading - time.time()
            if sleep_length > 0:
                time.sleep(sleep_length)


            #-------------------------------------------------------------------
            # Get loop start time
            #-------------------------------------------------------------------
            loop_start_time = datetime.datetime.now()
            logger.info('Loop start time: {start_time}'.format(
                start_time=loop_start_time.strftime('%Y-%m-%d %H:%M:%S')))


            #-------------------------------------------------------------------
            # Get rain fall measurement
            #-------------------------------------------------------------------
            if s.SENSOR_SET['precip_acc'][ENABLE]:
                
                #Calculate precip rate and reset it
                sensors['precip_rate'] = precip_tick_count * s.PRECIP_TICK_MEASURE
                precip_tick_count = 0.000000
                logger.info('Pricipitation counter RESET')
   
                #Get previous precip acc'ed value
                if rrdtool_enable_update:
                    data_values = []
                    last_precip_accu = None
                    tuple_location = 0
                    
                    #Fetch data from round robin database
                    data_values = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                                '-s', str(s.UPDATE_RATE * -2))

                    #Sync task time to rrd database
                    next_reading  = data_values[0][1]
                    logger.info('Next sensor reading at {time}'.format(
                        time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))
                    
                    #Extract time and precip acc value from fetched tuple
                    data_location = data_values[1].index('precip_acc'.replace(' ','_'))
                    while last_precip_accu is None and -tuple_location < len(data_values[2]):
                        tuple_location -= 1
                        last_precip_accu = data_values[2][tuple_location][data_location]
                        
                    last_entry_time = data_values[0][1] + (tuple_location * s.UPDATE_RATE)
                    
                    #If no data present, set it to 0
                    if last_precip_accu is None:
                        last_precip_accu = 0.00
                        
   
                #Previous reset time
                last_reset = loop_start_time.replace(hour=s.PRECIP_ACC_RESET_TIME[0], 
                                                        minute=s.PRECIP_ACC_RESET_TIME[1], 
                                                        second=s.PRECIP_ACC_RESET_TIME[2], 
                                                        microsecond=s.PRECIP_ACC_RESET_TIME[3])
    
                #Reset precip acc    
                time_since_last_reset = (loop_start_time - last_reset).total_seconds()
                time_since_last_feed_entry = time.mktime(loop_start_time.timetuple()) - last_entry_time
                if time_since_last_feed_entry > time_since_last_reset:
                    sensors['precip_acc'] = 0.00
                    logger.info('Pricipitation accumulated RESET')
                else:
                    sensors['precip_acc'] = last_precip_accu
                
                #Add previous precip. acc'ed value to current precip. rate
                sensors['precip_acc'] += sensors[s.PRECIP_RATE_NAME]
                
            else:
                # If rrdtool is disable just increment task time by rate
                next_reading += s.UPDATE_RATE
                logger.info('Next sensor reading at  {time}'.format(
                    time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))


            #-------------------------------------------------------------------
            # Add data to RRD
            #-------------------------------------------------------------------
            logger.info('Updating RRD file')

            try:
                rrdtool.update(s.RRDTOOL_RRD_FILE,
                    'N:{values}'.format(
                        values=':'.join([str(sensors[i]) for i in sorted(sensors)]))
            except rrdtool.error:
                logger.error('Failed to update RRD file ({value_error})'.format(
                    value_error=rrdtool.error))


    #---------------------------------------------------------------------------
    # User exit command
    #---------------------------------------------------------------------------
    except KeyboardInterrupt:

        logger.info('USER ACTION: End command')
        
        if screen_output:
            print('\nExiting program...')
        
        #Set pins to OFF state
        pi.write(s.LED_PIN, 0)

        #Stop processes
        rain_gauge.cancel()
        
        logger.info('--- Finished ---')
        

#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
