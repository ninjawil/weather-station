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
import urllib2
import json

# Third party modules

# Application modules
import rrd_tools
import maker_ch
import settings as s
import log
import check_process

WATERING_REC    = 24 # l/m^2

#===============================================================================
# GET LIST
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
# GET LIST
#===============================================================================
def get_forecast():
    f = urllib2.urlopen('http://api.wunderground.com/api/2bcf7f53ba4a77f5/forecast10day/q/pws:IASHBOUR2.json')  
    json_string = f.read()  
    f.close()
    return json.loads(json_string)  




#===============================================================================
# MAIN
#===============================================================================
def main():

    '''
    Grabs data from weather underground and rrd file to generate prediction
    for the amount of ground water.
    '''
   
   
    script_name = os.path.basename(sys.argv[0])


    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= s.SYS_FOLDER,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name))  


    #---------------------------------------------------------------------------
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    try:
        other_script_found = check_process.is_running(script_name)

        if other_script_found:
            logger.info('Script already runnning. Exiting...')
            logger.info(other_script_found)
            sys.exit()

    except Exception, e:
        logger.error('System check failed ({error_v}). Exiting...'.format(
            error_v=e))
        sys.exit()

    
    try:

        #-----------------------------------------------------------------------
        # CHECK RRD FILE
        #-----------------------------------------------------------------------
        rrd = rrd_tools.RrdFile('{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                                        fd2= s.DATA_FOLDER,
                                                        fl= s.RRDTOOL_RRD_FILE))
        
        sensors = list(s.SENSOR_SET.keys())

        if sorted(rrd.ds_list()) != sorted(sensors):
            logger.error('Data sources in RRD file does not match set up.')
            logger.error(rrd.ds_list())
            logger.error(sensors)
            logger.error('Exiting...')
            sys.exit()
        else:
            logger.info('RRD fetch successful.')



        #-----------------------------------------------------------------------
        # GET VALUES
        #-----------------------------------------------------------------------         
        # Fetch MIN values from rrd
        outside_max = get_list(rrd, 'MAX', 'outside_temp')
        logger.info('Out temp = {value}'.format(value= outside_max))        
        
        # Grab precip acc data
        precip = get_list(rrd, 'MAX', 'precip_acc')
        logger.info('Precip = {value}'.format(value= precip))

        # forecast = get_forecast()
        # forecast_high_temp  = [int(forecast['forecast']['simpleforecast']['forecastday'][i]['high']['celsius'])
        #                             for i in range(0, len(forecast['forecast']['simpleforecast']['forecastday'])) ]
        # forecast_precip     = [int(forecast['forecast']['simpleforecast']['forecastday'][i]['qpf_allday']['mm'])
        #                             for i in range(0, len(forecast['forecast']['simpleforecast']['forecastday'])) ]

        forecast_high_temp  = [20, 19, 19, 19, 19, 17, 16, 19, 19. 20]
        forecast_precip     = [3, 6, 5, 5, 6, 14, 1, 0, 6, 5]

        current_gw = 24

        drop_rate = {
            '0':    0,
            '10':   0.14,
            '20':   0.5,
            '30':   1}

        

        logger.info('Forecast high temp = {value}'.format(value= forecast_high_temp))
        logger.info('Forecast precip = {value}'.format(value= forecast_precip))




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
