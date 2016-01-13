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

# Third party modules

# Application modules
import log
import pyenergenie.src.ener314rt as ener314rt
import settings as s
import rrd_tools



#===============================================================================
# MAIN
#===============================================================================
def operate_switch(temp_on, temp_hys, sensors, rrd_res, rrd_file):
    
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
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= s.SYS_FOLDER,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name)) 
    

    #---------------------------------------------------------------------------
    # SET UP SENSOR VARIABLES
    #---------------------------------------------------------------------------  
    sensor_settings = collections.namedtuple('sensor_settings',
                                             'enable ref unit min max type')     
    sensor = {k: sensor_settings(*sensors[k]) for k in sensors}


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

        logger.info('Number of entries to update: {feeds}'.format(
                            feeds= len(rrd_entry.value)-2))

    except Exception, e:
        logger.error('RRD fetch failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()




    #-------------------------------------------------------------------
    # Get switch data
    #-------------------------------------------------------------------
    if sensor['sw_status'].enable or sensor['sw_power'].enable:
        try:
            switch = ener314rt.MiPlug()
            switch_data = switch.get_data()
            
            if switch_data['switch'] == 'U' or switch_data['real'] == 'U':
                raise ValueError
            else:
                logger.info('Reading value from switch data... OK')
                if sensor['sw_status'].enable:
                    sensor_value['sw_status'] = switch_data['switch']
                if sensor['sw_power'].enable:
                    sensor_value['sw_power']  = switch_data['real']

        except Exception, e:
            logger.warning('Failed to read switch data ({value_error})'.format(
                value_error=e), exc_info=True)
                
        finally:
            plug.close()



    #-------------------------------------------------------------------
    # Prepare to end script
    #-------------------------------------------------------------------
    logger.info('--- Read Sensors Finished ---')
    sys.exit()


#===============================================================================
# MAIN
#===============================================================================
def main():
    operate_switch( s.TEMP_HEATER_ON, s.TEMP_HYSTERISIS,
                    list(s.SENSOR_SET.keys()), 
                    s.UPDATE_RATE, 
                    '{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                            fd2= s.DATA_FOLDER,
                                            fl= s.RRDTOOL_RRD_FILE))


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
