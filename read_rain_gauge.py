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
import os
import sys
import threading
import time
import datetime
import logging
import collections

# Third party modules
import rrdtool
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
        
 

#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    global precip_tick_count
    global precip_accu
 
    precip_tick_count = 0
    precip_accu       = 0
    last_data_values  = []

    rrd_tuple = collections.namedtuple('rrd_tuple', 
        'start end step ds value') 


    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    log_file = 'logs/read_rain_gauge.log'
    logging.basicConfig(filename='{file_name}'.format(file_name=log_file), 
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.info('--- Read Rain Gauge Script Started ---')


    #---------------------------------------------------------------------------
    # LOAD DRIVERS
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
    if not os.path.exists(s.RRDTOOL_RRD_FILE):
        logger.info('RRD file not found. Exiting...')
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
    # SET UP RAIN SENSOR HARDWARE
    #---------------------------------------------------------------------------
    pi.set_mode(s.SENSOR_SET['precip_acc'][s.PIN_REF], pigpio.INPUT)
    rain_gauge = pi.callback(s.SENSOR_SET['precip_acc'][s.PIN_REF], 
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
            #Calculate precip rate and reset it
            sensors['precip_rate'] = precip_tick_count * s.PRECIP_TICK_MEASURE
            precip_tick_count = 0.000000
            logger.info('Pricipitation counter RESET')
            

            #Fetch data from round robin database
            rrd_data = []
            rrd_data = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                        '-s', str(s.UPDATE_RATE * -2))
            rrd_data = rrd_tuple(rrd_data[0][0], rrd_data[0][1], rrd_data[0][2], 
                                 rrd_data[1], rrd_data[2])


            #Sync task time to rrd database
            next_reading  = rrd_data.end
            

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
                    

            ##Reset precip acc 
            last_reset = loop_start_time.replace(hour=0, minute=0, second=0, microsecond=0)   
            secs_since_last_reset = (loop_start_time - last_reset).total_seconds()
            secs_since_last_feed_entry = time.mktime(loop_start_time.timetuple()) - last_entry_time
            if secs_since_last_feed_entry > secs_since_last_reset:
                sensors['precip_acc'] = 0.00
                logger.info('Pricipitation accumulated RESET')
            else:
                sensors['precip_acc'] = last_precip_accu
            
            
            #Add previous precip. acc'ed value to current precip. rate
            sensors['precip_acc'] += sensors['precip_rate']
                

            #-------------------------------------------------------------------
            # Add data to RRD
            #-------------------------------------------------------------------
            result = rrd_tools.update_rrd_file(s.RRDTOOL_RRD_FILE,sensors)

            if result == 'OK':
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
