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

'''Counts ticks from the reed switch of a rain gauge via an interrupt driven
    callback function. This count is stored in the precipiattion rate variable
    and is reset every loop.
    Script loops until stopped by the user.
    Data is stored to an RRD file at the update time pulled from the RRD file.
    Current precipitation accumulated value is pulled from the RRD file and 
    incremented by the counted ticks from the rain gauge.
    At midnight, the precipitation accumulated value is reset.
    If there is no RRD file or its set up is different from requirement, the 
    script will abort.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import sys
import threading
import time
import datetime
import log
import collections

# Third party modules
import pigpio

# Application modules
import settings as s
import rrd_tools


#===============================================================================
# GLOBAL VARIABLES
#===============================================================================
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
        logger.debug('Precip tick count : {tick}'.format(tick= precip_tick_count))
        
 

#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    global precip_tick_count
    global precip_accu
 
    precip_tick_count = 0
    precip_accu       = 0


    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = log.setup('root', '/home/pi/weather/logs/read_rain_gauge.log')
    
    logger.info('--- Read Rain Gauge Script Started ---')
    

    #---------------------------------------------------------------------------
    # LOAD DRIVERS
    #---------------------------------------------------------------------------
    try:
        pi = pigpio.pi()

    except ValueError:
        logger.critical('Failed to connect to PIGPIO ({error_v}). Exiting...'.format(
            error_v=ValueError))
        sys.exit()


    #---------------------------------------------------------------------------
    # CHECK RRD FILE AND SET UP SENSOR VARIABLES
    #---------------------------------------------------------------------------
    try:
        rrd = rrd_tools.rrd_file(s.RRDTOOL_RRD_FILE)
        
        if sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.critical('Data sources in RRD file does not match set up')
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

    logger.debug(sensor_value)
    logger.debug(sensor)


    #---------------------------------------------------------------------------
    # SET UP RAIN SENSOR HARDWARE
    #---------------------------------------------------------------------------
    pi.set_mode(sensor['precip_acc'].ref, pigpio.INPUT)
    rain_gauge = pi.callback(sensor['precip_acc'].ref, pigpio.FALLING_EDGE, 
                                count_rain_ticks)


    #---------------------------------------------------------------------------
    # TIMED LOOP
    #---------------------------------------------------------------------------
    try:
        while True:
            
            #-------------------------------------------------------------------
            # Delay to give update rate
            #-------------------------------------------------------------------
            next_reading  = rrd.next_update('LAST')

            logger.info('Next sensor reading at {time}'.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))
            
            sleep_length = next_reading - time.time()
            if sleep_length > 0:
                time.sleep(sleep_length)


            #-------------------------------------------------------------------
            # Get loop start time
            #-------------------------------------------------------------------
            loop_start_time = datetime.datetime.now()
            logger.debug('Loop start time: {start_time}'.format(
                start_time=loop_start_time.strftime('%Y-%m-%d %H:%M:%S')))


            #-------------------------------------------------------------------
            # Get rain fall measurement
            #-------------------------------------------------------------------
            #Calculate precip rate and reset it
            sensor_value['precip_rate'] = precip_tick_count * s.PRECIP_TICK_MEASURE
            precip_tick_count = 0.000000
            logger.debug('Precip tick counter RESET')
            

            #Fetch data from round robin database
            rrd_data = []
            rrd_tuple = collections.namedtuple( 'rrd_tuple', 
                                                'start end step ds value') 
            rrd_data = rrd.fetch('LAST', str(s.UPDATE_RATE * -2), 'now')
            rrd_data = rrd_tuple(rrd_data[0][0], rrd_data[0][1], rrd_data[0][2], 
                                 rrd_data[1], rrd_data[2])
            

            #Extract time and precip acc value from fetched tuple
            loc = 0
            last_precip_accu = None
            data_location = rrd_data.ds.index('precip_acc')
            while last_precip_accu is None and -loc < len(rrd_data.value):
                loc -= 1
                last_precip_accu = rrd_data.value[loc][data_location]
                
            last_entry_time = rrd_data.end + (loc * s.UPDATE_RATE)
            
            if last_precip_accu is None:
                last_precip_accu = 0.00

            logger.debug('Precip Acc from RRD = {rrd_precip_acc}'.format(
                rrd_precip_acc=last_precip_accu))
                    

            ##Reset precip acc at midnight
            last_reset = loop_start_time.replace(hour=0, minute=0, second=0, microsecond=0)   
            secs_since_last_reset = (loop_start_time - last_reset).total_seconds()
            secs_since_last_feed_entry = time.mktime(loop_start_time.timetuple()) - last_entry_time
            if secs_since_last_feed_entry > secs_since_last_reset:
                sensor_value['precip_acc'] = 0.00
                logger.info('Pricipitation accumulated RESET')
            else:
                sensor_value['precip_acc'] = last_precip_accu

            #Add previous precip. acc'ed value to current precip. rate
            sensor_value['precip_acc'] += sensor_value['precip_rate']
                

            #-------------------------------------------------------------------
            # Add data to RRD
            #-------------------------------------------------------------------
            logger.debug(sensor_value)

            if rrd.update_file(sensor_value) == 'OK':
                logger.info('Update RRD file OK')
            else:
                logger.error('Failed to update RRD file ({value_error})'.format(
                    value_error=result))


    #---------------------------------------------------------------------------
    # User exit command
    #---------------------------------------------------------------------------
    except KeyboardInterrupt:
        logger.info('USER ACTION: End command')
    
    finally:
        #Stop processes
        rain_gauge.cancel()
        
        logger.info('--- Finished ---')
        

#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
