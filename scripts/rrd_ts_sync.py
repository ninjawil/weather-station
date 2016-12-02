#!usr/bin/env python

#===============================================================================
# Import modules
#===============================================================================
# Standard Library
import os
import sys
import datetime
import time
import collections
import json

# Third party modules

# Application modules
import thingspeak.thingspeak as thingspeak
import rrd_tools
import settings as s
import log, logging
import check_process
import watchdog as wd


#===============================================================================
# SYNC
#===============================================================================
def sync(ts_host, ts_key, ts_channel_id, sensors, rrd_res, rrd_file, send_sync_err, err_file):

    '''
    Synchronizes thingspeak account with the data in the local Round Robin
        database.

    Starts by grabing some data from thingspeak to check all sensors are 
        present.

    Then checks all sensors are also present in the RRD database.

    If any of these checks fail, the script ends with an error.
    
    Inputs
        ts_host        - thingspeak host address
        ts_filename    - thingspeak file location with Write API Key
        ts_channel_id  - thingspeak channel id
        sensors        - list of names of each sensor
        rrd_res        - rrd resolution in seconds
        rrd_file       - rrd file location
        sync_err       - reporting of sync errors 
    '''
   
   
    #---------------------------------------------------------------------------
    # SET UP WATCHDOG & LOGGER
    #---------------------------------------------------------------------------
    logger = logging.getLogger('root')
    
    wd_err      = wd.ErrorCode(err_file, '0007')
    sync_err    = wd.ErrorCode(err_file, '0008')
  
    
    try:
        #-----------------------------------------------------------------------
        # SET UP THINGSPEAK ACCOUNT
        #-----------------------------------------------------------------------
        ts_acc = thingspeak.TSChannel(ts_host, api_key= ts_key, ch_id= ts_channel_id)
        
        ch_feed = ts_acc.get_a_channel_field_feed(field_id= 1, 
                                                parameters= {'results': 1})

        sensor_to_field = {}

        #Checks each sensor is present in thingspeak and if it is create a dict
        #with the field location of the sensor
        for sensor in sensors:
            if sensor.replace('_', ' ') not in ch_feed["channel"].values():
                logger.error('Data sources in the set up not present in thingspeak fields.')
                logger.error(ch_feed["channel"].values())
                logger.error(sensors)
                logger.error('Exiting...')
                wd_err.set()
                sys.exit()
            else:
                sensor_to_field[sensor] = ch_feed["channel"].keys()[ch_feed["channel"].values().index(sensor.replace('_', ' '))]
     
        logger.info(sensor_to_field)
        logger.info('Thingspeak fetch successful.')


        #-----------------------------------------------------------------------
        # CHECK RRD FILE
        #-----------------------------------------------------------------------
        rrd = rrd_tools.RrdFile(rrd_file)
                     
        #-----------------------------------------------------------------------
        # Get last feed update from thingspeak and RRD
        #-----------------------------------------------------------------------
        last_ts_feed = ts_acc.get_last_entry_in_channel_feed()
        last_rrd_feed = rrd.last_update()

        logger.debug('Last TS feed data:')
        logger.debug(last_ts_feed)

        #Thingspeak returns a -1 if there are no records
        if last_ts_feed == '-1':
            last_ts_feed = rrd_res
        else:
            last_ts_feed = datetime.datetime.strptime(last_ts_feed['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            last_ts_feed = int(time.mktime(last_ts_feed.utctimetuple()))
        
        logger.info('Last TS feed:  {last_ts_feed_time} {long_time}'.format(
            last_ts_feed_time= last_ts_feed,
            long_time= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(last_ts_feed))))

        logger.info('Last RRD feed: {last_ts_feed_time} {long_time}'.format(
            last_ts_feed_time= last_rrd_feed,
            long_time= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(last_rrd_feed))))
        
       
        #-----------------------------------------------------------------------
        # Fetch values from rrd
        #-----------------------------------------------------------------------
        rrd_entry = rrd.fetch(start= last_ts_feed - rrd_res)

        rt = collections.namedtuple( 'rt', 'start end step ds value')
        rrd_entry = rt(rrd_entry[0][0], rrd_entry[0][1], rrd_entry[0][2], 
                        rrd_entry[1], rrd_entry[2]) 

        logger.info('Number of entries to update: {feeds}'.format(
                            feeds= len(rrd_entry.value)-2))


        #-----------------------------------------------------------------------
        # Create a list with new thingspeak updates and send it to TS
        #-----------------------------------------------------------------------
        for i in range(1, len(rrd_entry.value)-1):
            next_entry_time = rrd_entry.start + ((i + 1) * rrd_res)
            
            tx_data = {'created_at': '{time}'.format(
                            time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_entry_time))),
                         'timezone':'Etc/UTC'}

            #Transmit data to be in the format {'field1': '18.232'} 
            for sensor in sorted(sensors):
                value = rrd_entry.value[i][rrd_entry.ds.index(sensor)]
                if value is not None:
                    tx_data[sensor_to_field[sensor]] = str(value)

            # Ignore entries without field entries
            if len(tx_data) > 2:
                logger.info(tx_data)
                response = ts_acc.update_channel(tx_data)
                logger.info('Thingspeak update: {reason}'.format(reason= response.reason))
                
                #Thingspeak update rate is limited to 15s per entry
                time.sleep(20)
                
                n = 0
                while response.status_code is not 200 and n < 3:
                    time.sleep(20)
                    response = ts_acc.update_channel(tx_data)
                    logger.error('Retry: {reason}'.format(reason= response.reason))
                    n += 1 

                if n >= 3:
                    logger.error('Failed to update Thingspeak. Exiting...')
                    if send_sync_err: sync_err.set()
                    sys.exit()          
                else:
                    #Thingspeak update rate is limited to 15s per entry
                    time.sleep(20)

        
        logger.info('--- Script Finished ---')


    except Exception, e:
        logger.error('Update failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        wd_err.set()
        sys.exit()


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''
    Passed arguments:
        --syncerr     - disables reporting of sync errors 
    '''

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
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    if check_process.is_running(script_name):
        logger.error('Script already running.')
        sys.exit()
            
    try:       
        #-------------------------------------------------------------------
        # Check and action passed arguments
        #-------------------------------------------------------------------
        sync_err = False
        if len(sys.argv) > 1:
            if '--syncerr' in sys.argv:
                logger.info('User requested NO ERROR feedback.')
                sync_err = True
 

        #-------------------------------------------------------------------
        # Get data from config file
        #-------------------------------------------------------------------               
        with open('{fl}/data/config.json'.format(fl= s.SYS_FOLDER), 'r') as f:
            config = json.load(f)

        ts_host_addr  = config['thingspeak']['THINGSPEAK_HOST_ADDR']
        ts_channel_id = config['thingspeak']['THINGSPEAK_CHANNEL_ID']
        ts_api_key    = config['thingspeak']['THINGSPEAK_API_KEY']

        
        #-------------------------------------------------------------------
        # Sync data
        #-------------------------------------------------------------------   
        sync(   ts_host_addr, 
                ts_api_key, 
                ts_channel_id,
                list(s.SENSOR_SET.keys()), 
                s.UPDATE_RATE, 
                '{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                        fd2= s.DATA_FOLDER,
                                        fl= s.RRDTOOL_RRD_FILE),
                sync_err,
                '{fl}/data/error.json'.format(fl= folder_loc))

    except Exception, e:
        logger.error('Update failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()



#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
