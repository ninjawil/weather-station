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
import rrd_tools
import maker_ch
import settings as s
import log
import check_process

#===============================================================================
# MAIN
#===============================================================================
def get_list(rrd_file, consolidation, data):
    '''
    Fetches previous 7 days values from rrd and returns it as a list.

    Any NaN values are ignored and not included in the list.
    '''

    rrd_entry = rrd_file.fetch(cf= consolidation, start='e-6d', end='-1d', res='86400')
        
    rt = collections.namedtuple( 'rt', 'start end step ds value')
    rrd_entry = rt(rrd_entry[0][0], rrd_entry[0][1], rrd_entry[0][2], 
                        rrd_entry[1], rrd_entry[2]) 

    data_length = len(rrd_entry.value)

    return [rrd_entry.value[i][rrd_entry.ds.index(data)] 
                    for i in range(0,data_length) if rrd_entry.value[i][rrd_entry.ds.index(data)] is not None]



#===============================================================================
# MAIN
#===============================================================================
def main():

    '''
    Grabs data from rrd file, calculates weekly minimun and average outside 
    temperature and total precipitation then sends it via maker channel.
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
        logger.info('Script already runnning. Exiting...')
        logger.info(other_script_found)
        sys.exit()  


    #---------------------------------------------------------------------------
    # Check RRD File
    #---------------------------------------------------------------------------
    rrd = rrd_tools.RrdFile('{fd1}/data/{fl}'.format(fd1= folder_loc,
                                                    fl= s.RRDTOOL_RRD_FILE))
        
    if not rrd.check_ds_list_match(list(s.SENSOR_SET.keys())):
        logger.error('Data sources in RRD file does not match set up.')
        logger.error('Exiting...')
        sys.exit()

    #-------------------------------------------------------------------
    # Get data from config file
    #-------------------------------------------------------------------
    try:
        with open('{fl}/data/config.json'.format(fl= s.SYS_FOLDER), 'r') as f:
            config = json.load(f)

        maker_ch_addr  = config['maker_channel']['MAKER_CH_ADDR']
        maker_ch_key   = config['maker_channel']['MAKER_CH_KEY']
        
    except Exception, e:
        logger.error('Failed to load config data ({error_v}). Exiting...'.format(
        error_v=e))
        sys.exit()

    
    try:
  
        #-----------------------------------------------------------------------
        # GET VALUES
        #-----------------------------------------------------------------------         
        # Fetch MIN values from rrd
        outside_min = min(get_list(rrd, 'MIN', 'outside_temp'))
        logger.info('Outside MIN temp = {value}'.format(value= outside_min))
        
        # Fetch AVG values from rrd
        temp_list = get_list(rrd, 'AVERAGE', 'outside_temp')        
        outside_avg = sum(temp_list) / float(len(temp_list))
        logger.info('Outside AVG temp = {value}'.format(value= outside_avg))

        # Grab precip acc data
        precip_tot = sum(get_list(rrd, 'MAX', 'precip_acc'))
        logger.info('Precip TOTAL temp = {value}'.format(value= precip_tot))


        #-----------------------------------------------------------------------
        # SEND VALUES VIA MAKER CHANNEL
        #-----------------------------------------------------------------------
        mc = maker_ch.MakerChannel(maker_ch_addr, maker_ch_key, 'WS_weekly_report')
        mc.trigger_an_event(value1= '{0:.2f}'.format(outside_avg), 
                            value2= '{0:.2f}'.format(outside_min), 
                            value3= '{0:.2f}'.format(precip_tot))

        logger.info('--- Script Finished ---')


    except Exception, e:
        logger.error('Update failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()

    
#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
