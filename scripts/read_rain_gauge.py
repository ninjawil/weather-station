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
import collections
import json

# Third party modules
import pigpio

# Application modules
import log
import logging
import settings as s
import rrd_tools
import check_process
import watchdog


#===============================================================================
# GLOBAL VARIABLES
#===============================================================================
last_rising_edge = None



#===============================================================================
# FLOAT COMPARISON
#===============================================================================
def approx_equal(a, b, tol=0.0001):
     return abs(a - b) < tol


#===============================================================================
# EDGE CALLBACK FUNCTION TO COUNT RAIN TICKS
#===============================================================================
def count_rain_ticks(gpio, level, tick):
    
    '''Count the ticks from a reed switch'''
    
    global precip_tick_count
    global last_rising_edge

    logger = logging.getLogger('root')
    
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
        with open('{fd1}/data/tick_count'.format(fd1= s.SYS_FOLDER), 'w') as f:
            f.write('{tick_time}:{tick_count}'.format(
                                tick_time=int(datetime.datetime.now().strftime("%s")),
                                tick_count=int(precip_tick_count)))
        
 

#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    global precip_tick_count
    global precip_accu

    precip_tick_count = 0
    precip_accu       = 0

    script_name = os.path.basename(sys.argv[0])
    folder_loc  = os.path.dirname(os.path.realpath(sys.argv[0]))
    folder_loc  = folder_loc.replace('scripts', '')


    #---------------------------------------------------------------------------
    # SET UP LOGGER AND WATCHDOG
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= s.SYS_FOLDER,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name))


    #---------------------------------------------------------------------------
    # SET UP WATCHDOG
    #---------------------------------------------------------------------------
    err_file    = '{fl}/data/error.json'.format(fl= folder_loc)
    wd_counter  = wd.ErrorCode(err_file, '0001')    # Script READ_RAIN_GAUGE stopped
    wd_err      = wd.ErrorCode(err_file, '0002')    # Script READ_RAIN_GAUGE error
    wd_acc_err  = wd.ErrorCode(err_file, '0004')    # Accumulate precipitation failed


    #---------------------------------------------------------------------------
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    if check_process.is_running(script_name):
        wd_err.set()
        sys.exit()


    #---------------------------------------------------------------------------
    # LOAD DRIVERS
    #---------------------------------------------------------------------------
    try:
        pi = pigpio.pi()

    except Exception, e:
        logger.error('Failed to connect to PIGPIO ({error_v}). Exiting...'.format(
            error_v=e))
        wd_err.set()
        sys.exit()


    #---------------------------------------------------------------------------
    # INITIATE CHECKS
    #---------------------------------------------------------------------------
    try:

        #-----------------------------------------------------------------------
        # CHECK RRD FILE AND SET UP WATCHDOG
        #-----------------------------------------------------------------------
        rrd = rrd_tools.RrdFile('{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                                            fd2= s.DATA_FOLDER,
                                                            fl= s.RRDTOOL_RRD_FILE))
            
        if not rrd.check_ds_list_match(list(s.SENSOR_SET.keys())):
            wd_err.set()
            sys.exit()


        #-----------------------------------------------------------------------
        # SET UP SENSOR VARIABLES
        #-----------------------------------------------------------------------
        sensor_value = {x: 'U' for x in s.SENSOR_SET}

        ss = collections.namedtuple('ss', 'enable ref unit min max type')
        sensor = {k: ss(*s.SENSOR_SET[k]) for k in s.SENSOR_SET}
        
        logger.debug(sensor_value)


        #-----------------------------------------------------------------------
        # CHECK FOR PREVIOUS TICK COUNTS
        #-----------------------------------------------------------------------
        filename = '{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                          fd2= s.DATA_FOLDER,
                                          fl= s.TICK_DATA)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                data = f.read()
                tick_time, tick_count = data.split(':')

            if (rrd.next_update() - int(tick_time)) <= s.UPDATE_RATE:
                precip_tick_count = int(tick_count)
                logger.info('Recent tick data found. Current count = {tick}'.format(tick= precip_tick_count))


        #-----------------------------------------------------------------------
        # SET UP RAIN SENSOR HARDWARE
        #-----------------------------------------------------------------------
        pi.set_mode(sensor['precip_acc'].ref, pigpio.INPUT)
        rain_gauge = pi.callback(sensor['precip_acc'].ref, pigpio.FALLING_EDGE, 
                                    count_rain_ticks)


        #-----------------------------------------------------------------------
        # TIMED LOOP
        #-----------------------------------------------------------------------
        while True:


            #-------------------------------------------------------------------
            # Increment watchdog counter
            #-------------------------------------------------------------------
            wd_counter.increment_counter(step= 1)


            #-------------------------------------------------------------------
            # Delay to give update rate
            #-------------------------------------------------------------------
            next_reading  = rrd.next_update()
            logger.debug('Next sensor reading at {time}'.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))

            sleep_length = next_reading - time.time()
            if sleep_length > 0:
                time.sleep(sleep_length)


            #-------------------------------------------------------------------
            # Get loop start time
            #-------------------------------------------------------------------
            loop_start = datetime.datetime.utcnow()
            logger.info('*** Loop start time: {start_time} ***'.format(
                            start_time=loop_start.strftime('%Y-%m-%d %H:%M:%S')))


            #-------------------------------------------------------------------
            # Get data from config file
            #-------------------------------------------------------------------
            try:
                with open('{fl}/data/config.json'.format(fl= s.SYS_FOLDER), 'r') as f:
                            config = json.load(f)

                tick_measure   = config['rain_gauge']['PRECIP_TICK_MEASURE']
                logger.info(u'Rain gauge tick {meas}mm'.format(meas= tick_measure))

            except Exception, e:
                logger.critical('Failed to get config data ({value_error})'.format(
                    value_error=e), exc_info=True)
                wd_err.set()
                sys.exit()


            #-------------------------------------------------------------------
            # Get rain fall measurement
            #-------------------------------------------------------------------
            sensor_value['precip_acc'] = 0.00
            sensor_value['precip_rate'] = precip_tick_count * tick_measure
            precip_tick_count = 0.00
            logger.debug('Precip tick counter RESET')
            

            #If last entry was before midnight this morning do not use accumulated
            # precipitation value taken from round robin database
            last_entry_time = rrd.last_update()

            last_reset = loop_start.replace(hour=0, minute=0, second=0, microsecond=0)   
            last_reset = int(time.mktime(last_reset.utctimetuple()))
            tdelta = last_entry_time - last_reset

            logger.debug('last entry = {l_entry}'.format(l_entry= last_entry_time))
            logger.debug('last_reset = {l_reset_t}'.format(l_reset_t= last_reset))
            logger.debug('tdelta = {delta_t}'.format(delta_t= tdelta))

            if tdelta >= 0.00:
                try:
                    #Fetch today's data from round robin database
                    data = []
                    data = rrd.fetch(start=last_reset, 
                                     end=last_entry_time)

                    rt = collections.namedtuple( 'rt', 'start end step ds value')
                    data = rt(data[0][0], data[0][1], data[0][2], 
                                            data[1], data[2])


                    #Create list with today's precip rate values
                    loc = data.ds.index('precip_rate')
                    todays_p_rate = [data.value[i][loc] for i in range(0, len(data.value)-1)]

                    #Get second to last entry as last entry is next update
                    sensor_value['precip_acc'] = float(
                        data.value[len(data.value)-2][data.ds.index('precip_acc')] or 0)
                    logger.debug('Last value: {v}'.format(v= sensor_value['precip_acc']))
                    
                    logger.debug('Todays p rate')
                    logger.debug(todays_p_rate)
                    
                    #If any values missing from today, prevent accumulation
                    if None not in todays_p_rate:
                        logger.debug('Sum of todays Precip_rate: {p_rate}'.format(p_rate= sum(todays_p_rate)))
                        sensor_value['precip_acc'] = sum(todays_p_rate) + sensor_value['precip_rate']
                    else:
                        logger.error('Values missing in todays precip rate')
                        sensor_value['precip_acc'] = 'U'

                except Exception, e:
                    logger.error('Accumulate precipitation failed ({error_v}). Exiting...'.format(
                        error_v=e))
                    wd_acc_err.set()


            #Round values
            if sensor_value['precip_rate'] is not 'U':
                sensor_value['precip_rate'] = float('{0:.3f}'.format(sensor_value['precip_rate']))           
            if sensor_value['precip_acc'] is not 'U':
                sensor_value['precip_acc'] = float('{0:.3f}'.format(sensor_value['precip_acc']))
            
            #Log values
            logger.info('Precip_acc:  {precip_acc}'.format(
                                        precip_acc= sensor_value['precip_acc']))
            logger.info('Precip_rate: {precip_rate}'.format(
                                        precip_rate= sensor_value['precip_rate']))
                

            #-------------------------------------------------------------------
            # Add data to RRD
            #-------------------------------------------------------------------
            logger.debug('Update time = {update_time}'.format(update_time= next_reading))
            logger.debug([v for (k, v) in sorted(sensor_value.items()) if v != 'U'])
            
            result = rrd.update_file(timestamp= next_reading,
                ds_name= [k for (k, v) in sorted(sensor_value.items()) if v!='U'],
                values= [v for (k, v) in sorted(sensor_value.items()) if v != 'U'])

            if result == 'OK':
                logger.info('Update RRD file OK')
            else:
                logger.error('Failed to update RRD file ({value_error})'.format(
                    value_error=result))
                logger.error(sensor_value)
                wd_err.set()


    #---------------------------------------------------------------------------
    # User exit command
    #---------------------------------------------------------------------------
    except KeyboardInterrupt:
        logger.info('USER ACTION: End command')
        wd_err.set()
        sys.exit()


    #---------------------------------------------------------------------------
    # Other error captured
    #---------------------------------------------------------------------------
    except Exception, e:
        logger.error('Script Error', exc_info=True)
        wd_err.set()
        sys.exit()


    #---------------------------------------------------------------------------
    # Stop processes
    #---------------------------------------------------------------------------
    finally:
        rain_gauge.cancel()
        logger.info('--- Read Rain Gauge Finished ---')
        

#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())