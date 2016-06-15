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
        logger.error('Script already runnning. Exiting...')
        logger.error(other_script_found)
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
        with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
            config = json.load(f)

        water_level_alarm       = config['water_level']['ALARM_ENABLE']
        recommended_watering    = config['water_level']['RECOMMENDED_WATERING']
        days                    = config['water_level']['RECOMMENDED_WATERING_DAYS']
        ground_water_saturation = config['water_level']['GRND_WATER_SATURATION']
        
        dry_rate = [0,0,0,0]
        dry_rate[0]             = config['water_level']['DRY_RATE_0_9']
        dry_rate[1]             = config['water_level']['DRY_RATE_10_19']
        dry_rate[2]             = config['water_level']['DRY_RATE_20_29']
        dry_rate[3]             = config['water_level']['DRY_RATE_30_UP']
        
        # Calculate matrix how quickly ground dries depending on temp
        dry_rate[:] = [x*recommended_watering for x in dry_rate]
        
    except Exception, e:
        logger.error('Unable to load config data. Exiting...')
        sys.exit()


    try:

        #-----------------------------------------------------------------------
        # Calculate current ground water level if no gw_level file
        #----------------------------------------------------------------------- 
        try:
            with open('{fl}/data/gw_level.json'.format(fl= folder_loc), 'r') as f:
                gw_data = json.load(f)

            ground_water_level = gw_data['gw_prediction'][0]

            logger.info('Water level file found. Getting starting')
            logger.info('GW level = {value}'.format(value= ground_water_level)) 

            # Fetch MIN values from rrd
            outside_max = get_list(rrd, 'MAX', 'outside_temp')
            
            # Grab precip acc data
            precip = get_list(rrd, 'MAX', 'precip_acc')


            
        except Exception, e:
            logger.info('Water level file not found.')
            logger.info('Using 24 l/m^2 as a starting value.')
            ground_water_level = 24



 
        # for i in range(0, len(outside_max)):
        #     if outside_max[i] < 9:
        #         rate = dry_rate[0]
        #     elif outside_max[i] < 19:
        #         rate = dry_rate[1]
        #     elif outside_max[i] < 29:
        #         rate = dry_rate[2]
        #     else:
        #         rate = dry_rate[3]

        #     ground_water_level =  ground_water_level + precip[i] - rate

        # if ground_water_level > ground_water_saturation:
        #     ground_water_level = ground_water_saturation
    
        logger.info('Out temp = {value}'.format(value= outside_max[-1]))        
        logger.info('Precip = {value}'.format(value= precip[-1])) 


        #-----------------------------------------------------------------------
        # Grab weather prediction data from online
        #----------------------------------------------------------------------- 
        forecast = {}
        # web_forecast = get_forecast()
        # forecast['high_temp']  = [int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['high']['celsius'])
        #                             for i in range(0, len(web_forecast['forecast']['simpleforecast']['forecastday'])) ]
        # forecast['precip']     = [int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['qpf_allday']['mm'])
        #                             for i in range(0, len(web_forecast['forecast']['simpleforecast']['forecastday'])) ]
        
        watering = 0

        forecast =  {
                        'high_temp':        [20, 19, 19, 19, 19, 17, 16, 19, 19, 20],
                        'precip':           [0, 6, 5, 5, 6, 14, 1, 0, 6, 5],
                        'precip_chance':    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                    }


        # Calculate possible precipitation
        forecast['precip'][:] = [forecast['precip'][i]*forecast['precip_chance'][i] 
                                                for i in range(0, len(forecast['precip']))]


        #-----------------------------------------------------------------------
        # Calculate predicted ground water level for next few days
        #----------------------------------------------------------------------- 
        forecast['gw_prediction'] = [0 for i in range(0, days)]           
        forecast['gw_prediction'][0] = ground_water_level + watering  

        for i in range(0, days-1):
            if forecast['high_temp'][i] <= 9:
                rate = dry_rate[0]
            elif forecast['high_temp'][i] <= 19:
                rate = dry_rate[1]
            elif forecast['high_temp'][i] <= 29:
                rate = dry_rate[2]
            else:
                rate = dry_rate[3]

            forecast['gw_prediction'][i+1] =  forecast['gw_prediction'][i] + forecast['precip'][i] - rate

            # Limit value if saturated
            if forecast['gw_prediction'][i+1] > ground_water_saturation:
                forecast['gw_prediction'][i+1] = ground_water_saturation


        logger.info('Forecast high temp = {value}'.format(value= forecast['high_temp']))
        logger.info('Forecast precip = {value}'.format(value= forecast['precip']))
        logger.info('Forecast gw = {value}'.format(value= forecast['gw_prediction']))


        #-----------------------------------------------------------------------
        # Write water level data file
        #----------------------------------------------------------------------- 
        with open('{fl}/data/gw_level.json'.format(fl= folder_loc), 'w') as f:
            json.dump(forecast, f)



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
