#!/usr/bin/env python

''' Script checks the last value of the inside temperature in the rrd file
    and turns on or off the heater via the MiPlug'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import time
import collections
from ConfigParser import SafeConfigParser

# Third party modules

# Application modules
import log
import pyenergenie.ener314rt as ener314rt
import settings as s
import rrd_tools



#===============================================================================
# MAIN
#===============================================================================
def operate_switch(temp_on, temp_hys, sensors, switch_id, rrd_res, rrd_file):
    
    '''
    Operates a MiPlug switch depending on the last temperature value entered
    in a rrd file.
    
    Inputs
        temp_on        - temperature to switch ON plug
        temp_hys       - temperature hysterisis
        sensors        - list of names of each sensor
        rrd_res        - rrd resolution in seconds
        rrd_file       - rrd file location
    '''


    script_name = os.path.basename(sys.argv[0])

    #---------------------------------------------------------------------------
    # Set up logger
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/{script}.log'.format(
                                                    folder= log_folder,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name)) 
    

    try:
        #-----------------------------------------------------------------------
        # CHECK RRD FILE
        #-----------------------------------------------------------------------
        rrd = rrd_tools.RrdFile(rrd_file)
        
        if sorted(rrd.ds_list()) != sorted(sensors):
            logger.error('Data sources in RRD file does not match set up.')
            logger.error(rrd.ds_list())
            logger.error(sensors)
            logger.error('Exiting...')
            sys.exit()
        else:
            logger.info('RRD fetch successful.')

        #-----------------------------------------------------------------------
        # Get last feed update from RRD
        #-----------------------------------------------------------------------
        last_rrd_feed = rrd.last_update()
        
        logger.info('Last RRD feed: {last_ts_feed_time} {long_time}'.format(
            last_ts_feed_time= last_rrd_feed,
            long_time= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(last_rrd_feed))))

        #-----------------------------------------------------------------------
        # Fetch values from rrd
        #-----------------------------------------------------------------------
        rrd_entry = rrd.fetch(start= last_rrd_feed - rrd_res)

        rt = collections.namedtuple( 'rt', 'start end step ds value')
        rrd_entry = rt(rrd_entry[0][0], rrd_entry[0][1], rrd_entry[0][2], 
                        rrd_entry[1], rrd_entry[2]) 

        # Grab the last inside temperature value
        inside_temp = float(
            rrd_entry.value[len(rrd_entry.value)-2][rrd_entry.ds.index('inside_temp') or 0])

        logger.info(u'Inside temperature is {temp}\u00B0C'.format(temp= inside_temp))

    except Exception, e:
        logger.error('RRD fetch failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()


    #-------------------------------------------------------------------
    # Operate switch
    #-------------------------------------------------------------------
    try:
        switch = ener314rt.MiPlug(sensorid= switch_id)

        # Turn ON/OFF heater depending on inside temp value from RRD
        if inside_temp < (temp_on + temp_hys):
            switch.send_data(True)
            logger.info('Switch turned ON')

        elif inside_temp > (temp_on - temp_hys):
            switch.send_data(False)
            logger.info('Switch turned OFF')         
       
    except Exception, e:
        logger.warning('Failed to set switch ({value_error})'.format(
            value_error=e), exc_info=True)
            
    finally:
        switch.close()


    #-------------------------------------------------------------------
    # Prepare to end script
    #-------------------------------------------------------------------
    logger.info('--- Read Sensors Finished ---')
    sys.exit()


#===============================================================================
# MAIN
#===============================================================================
def main():

    #---------------------------------------------------------------------------
    # SET UP SENSOR VARIABLES
    #---------------------------------------------------------------------------  
    sensor_settings = collections.namedtuple('sensor_settings',
                                             'enable ref unit min max type')     
    sensor = {k: sensor_settings(*s.SENSOR_SET[k]) for k in s.SENSOR_SET}


    #-------------------------------------------------------------------
    # Get data from config file
    #-------------------------------------------------------------------
    try:
        config = SafeConfigParser()
        config.read('../config.ini')
        on_temp  = config.getfloat('heater', 'TEMP_HEATER_ON')
        hys_temp = config.getfloat('heater', 'TEMP_HYSTERISIS')
        switch_id = config.getint('heater', 'MIPLUG_SENSOR_ID')

    except Exception, e:
        print(e)
        sys.exit()


    #-----------------------------------------------------------------------
    # OPERATE SWITCH IF ENABLED
    #-----------------------------------------------------------------------
    if sensor['sw_status'].enable or sensor['sw_power'].enable:
        operate_switch( on_temp, 
                        hys_temp,
                        list(s.SENSOR_SET.keys()),
                        switch_id, 
                        s.UPDATE_RATE, 
                        '{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                                fd2= s.DATA_FOLDER,
                                                fl= s.RRDTOOL_RRD_FILE))


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
