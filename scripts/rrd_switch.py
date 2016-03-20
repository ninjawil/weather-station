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
import json

# Third party modules

# Application modules
import log, logging
import pyenergenie.ener314rt as ener314rt
import settings as s
import rrd_tools
import watchdog as wd



#===============================================================================
# MAIN
#===============================================================================
def operate_switch( temp_threshold, temp_hys, force_on, sensors, switch_id, 
                    rrd_res, rrd_file, err_code):
    
    '''
    Operates a MiPlug switch depending on the last temperature value entered
    in a rrd file.
    
    Inputs
        temp_threshold - temperature to switch ON plug
        temp_hys       - temperature hysterisis
        sensors        - list of names of each sensor
        rrd_res        - rrd resolution in seconds
        rrd_file       - rrd file location
    ''' 

    logger = logging.getLogger('root')   

    try:
        #-----------------------------------------------------------------------
        # CHECK RRD FILE
        #-----------------------------------------------------------------------
        rrd = rrd_tools.RrdFile(rrd_file)
        
        if not rrd.check_ds_list_match(sensors):
            wd_err.set()
            sys.exit()

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
        inside_temp = (rrd_entry.value[len(rrd_entry.value)-2][rrd_entry.ds.index('inside_temp') or 0])

        if not inside_temp:
            logger.info('No previous inside temperature reading. Exiting...')
            sys.exit()

        inside_temp = float(inside_temp)

        logger.info(u'Threshold {temp_thresh}\u00B0C \u00B1 {temp_hyst}\u00B0C'.format(
            temp_thresh= temp_threshold,
            temp_hyst= temp_hys))
        logger.info(u'Inside temperature is {temp}\u00B0C'.format(temp= inside_temp))
        if force_on:
            logger.info('User force ON switch')

    except Exception, e:
        logger.critical('RRD fetch failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        wd_err.set()
        sys.exit()


    #-------------------------------------------------------------------
    # Operate switch
    #-------------------------------------------------------------------
    try:
        switch = ener314rt.MiPlug(sensorid= switch_id)

        # Turn ON/OFF heater depending on inside temp value from RRD
        if force_on or inside_temp <= (temp_threshold - temp_hys):
            switch.send_data(True)
            logger.info('Switch turned ON')

        elif inside_temp >= (temp_threshold + temp_hys):
            switch.send_data(False)
            logger.info('Switch turned OFF')         
       
    except Exception, e:
        logger.warning('Failed to set switch ({value_error})'.format(
            value_error=e), exc_info=True)
        wd_err.set()
            
    finally:
        switch.close()


#===============================================================================
# MAIN
#===============================================================================
def main():


    script_name = os.path.basename(sys.argv[0])
    folder_loc  = os.path.dirname(os.path.realpath(sys.argv[0]))
    folder_loc  = folder_loc.replace('scripts', '')


    #---------------------------------------------------------------------------
    # Set up logger
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= folder_loc,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name)) 
 

    #---------------------------------------------------------------------------
    # SET UP WATCHDOG
    #---------------------------------------------------------------------------
    err_file    = '{fl}/data/error.json'.format(fl= folder_loc)
    wd_err      = wd.ErrorCode(err_file, '0005')


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
        with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
            config = json.load(f)

        sw_user_enable  = config['heater']['HEATER_ENABLE']
        sw_user_force   = config['heater']['HEATER_FORCE_ON']
        on_temp         = config['heater']['TEMP_HEATER_ON']
        hys_temp        = config['heater']['TEMP_HYSTERISIS']
        switch_id       = config['heater']['MIPLUG_SENSOR_ID']

    except Exception, e:
        logger.error('Could not load config data ({error_v})'.format(
            error_v=e), exc_info=True)
        wd_err.set()
        sys.exit()


    #-----------------------------------------------------------------------
    # OPERATE SWITCH IF ENABLED
    #-----------------------------------------------------------------------
    if sw_user_enable:
        if sensor['sw_status'].enable or sensor['sw_power'].enable:
            operate_switch( on_temp, 
                            hys_temp,
                            sw_user_force,
                            list(s.SENSOR_SET.keys()),
                            switch_id, 
                            s.UPDATE_RATE, 
                            '{fd1}/data/{fl}'.format(fd1= folder_loc,
                                                     fl= s.RRDTOOL_RRD_FILE),
                            wd_err)
    # If user enable is DISABLED switch OFF heater
    else:
        logger.info('User enable set to DISABLED')
        try:
            switch = ener314rt.MiPlug(sensorid= switch_id)
            switch.send_data(False)      
           
        except Exception, e:
            logger.warning('Failed to set switch ({value_error})'.format(
                value_error=e), exc_info=True)
            wd_err.set()
                
        finally:
            switch.close()

    logger.info('--- Read Sensors Finished ---')


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
