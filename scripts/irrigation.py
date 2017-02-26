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
import math

# Third party modules

# Application modules
import rrd_tools
import maker_ch
import settings as s
import log
import check_process


#===============================================================================
# GET WEATHER FORECAST
#===============================================================================
def get_forecast():
    f = urllib2.urlopen('http://api.wunderground.com/api/2bcf7f53ba4a77f5/forecast10day/q/pws:IASHBOUR2.json')  
    json_string = f.read()  
    f.close()
    return json.loads(json_string)  


#===============================================================================
# Calculate extraterrestrial radiation for daily periods (Ra)
#===============================================================================
def ra_calc(j, lat_rad):

    ''' 
    Calculating the Extraterrestrial radiation for daily periods in MJ/m^2/day

    Inputs are 
         j           - number of the day in the year between 1 (1 January) and 365 
                     or 366 (31 December)
         lat_rad     - latitude of location in radians
    '''

    #-----------------------------------------------------------------------
    # Calculate Extraterrestrial radiation for daily periods (Ra)
    #----------------------------------------------------------------------- 
    # Solar declination (sigma) [rad]
    sigma =0.409 * math.sin(0.0172 * j - 1.39)

    # Sunset hour angle (ws) [rad]
    ws = math.acos(-math.tan(lat_rad) * math.tan(sigma))

    # Inverse relative distance Earth-Sun (dr)
    dr = 1 + 0.033 * math.cos(0.0172 * j)

    # Extraterrestrial radiation for daily periods (Ra) [MJ/m^2/d]
    ra = 37.6 * dr * (ws * math.sin(lat_rad) * math.sin(sigma) + math.cos(lat_rad) * math.cos(sigma) * math.sin(ws))

    # Re [J/m^2/d]
    return ra



#===============================================================================
# Calculate reference evapotranspiration value
#===============================================================================
def eto_tbase_calc(re, temp_mean):

    ''' 
    Function uses temperature-based (T-based) PE formulation suggested by Oudin et al (2005).

    PET in units of mm/s

    Inputs are 
         Re          - extraterrestrial radiation (J/m2/s)
         temp_mean   - mean temperature *C
    '''

    #---------------------------------------------------------------------------
    # Constants
    #---------------------------------------------------------------------------
    LATENT_HEAT_FLUX        = 2450000   # MJ/kg
    WATER_DENSITY           = 1000      # kg/m^3

    #---------------------------------------------------------------------------
    # Calculate ETo
    #--------------------------------------------------------------------------- 
    # Temperature-based (T-based) PE formulation suggested by Oudin et al (2005)
    if temp_mean + 5 > 0:
        return (1000 * re * (temp_mean + 5)) / (100*(LATENT_HEAT_FLUX * WATER_DENSITY))
    else:
        return 0


#===============================================================================
# Calculate Effective Rainfall
#===============================================================================
def effective_rainfall_calc(p):

    ''' Effective Rainfall converted from FAO monthly values'''

    if p > 0.67:
        return (0.7432 * p) - 0.5
    else:
        return 0


#===============================================================================
# Calculate Readily Available Water level
#===============================================================================
def readily_available_water_calc(soil_type, root_depth, etc, depletion_fraction= 0.5):

    ''' 
    Calculates the Total Available Water and Readily Available Water (RAW) 
    value in mm

    See http://www.fao.org/docrep/X0490E/x0490e0e.htm#chapter 8   etc under soil water stress conditions
    '''

    soils = {
        'sand':             {'theta_fc': 0.12,   'theta_wp': 0.05 },
        'loamy sand':       {'theta_fc': 0.15,   'theta_wp': 0.07 },
        'sandy loam':       {'theta_fc': 0.23,   'theta_wp': 0.11 },
        'loam':             {'theta_fc': 0.25,   'theta_wp': 0.12 },
        'silt loam':        {'theta_fc': 0.29,   'theta_wp': 0.12 },
        'silt':             {'theta_fc': 0.32,   'theta_wp': 0.17 },
        'silt clay loam':   {'theta_fc': 0.34,   'theta_wp': 0.21 },
        'silty loam':       {'theta_fc': 0.36,   'theta_wp': 0.23 },
        'clay':             {'theta_fc': 0.36,   'theta_wp': 0.22 }
    }

    taw = 1000 * (soils[soil_type]['theta_fc']-soils[soil_type]['theta_wp']) * root_depth

    raw = depletion_fraction * taw

    return taw, raw



#===============================================================================
# Linear Regression calculation
#===============================================================================
def linear_regression(x_list, y_list):

    '''
    Calculate linear regression formula.
    Returns the m and c in y=mx+c
    '''

    x_mean = sum(x_list) / len(x_list)
    y_mean = sum(y_list) / len(y_list)

    x_avgx          = [x - x_mean for x in x_list]
    y_avgy          = [y - y_mean for y in y_list]

    m = sum([x*y for x,y in zip(x_avgx, x_avgx)]) / sum([x**2 for x in x_avgx])

    c = y_mean - m*x_mean

    return m,c



#===============================================================================
# MAIN
#===============================================================================
def main():

    '''
    Grabs data from weather underground and rrd file to generate prediction
    for the water depth
    '''
   
    script_name = os.path.basename(sys.argv[0])
    folder_loc  = os.path.dirname(os.path.realpath(sys.argv[0]))
    folder_loc  = folder_loc.replace('scripts', '')


    #---------------------------------------------------------------------------
    # SET UP LOGGER
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
    # CHECK RRD FILE
    #---------------------------------------------------------------------------
    rrd = rrd_tools.RrdFile('{fd1}/data/{fl}'.format(fd1= folder_loc,
                                                    fl= s.RRDTOOL_RRD_FILE))
        
    if not rrd.check_ds_list_match(list(s.SENSOR_SET.keys())):
        logger.error('Data sources in RRD file does not match set up.')
        logger.error('Exiting...')
        sys.exit()


    #-------------------------------------------------------------------
    # GET DATA FROM CONFIG FILE
    #-------------------------------------------------------------------
    try:
        with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
            config = json.load(f)

        location                = [config['irrigation']['COORD_NORTH'], config['irrigation']['COORD_SOUTH']]
        alarm_enable            = config['irrigation']['ALARM_ENABLE']
        alarm_level             = config['irrigation']['ALARM_LEVEL']
        kc                      = config['irrigation']['CROP_FACTOR_KC']
        days                    = config['irrigation']['RECOMMENDED_WATERING_DAYS']
        root_depth              = config['irrigation']['ROOT_DEPTH']
        soil_type               = config['irrigation']['SOIL_TYPE']
        irrig_full              = config['irrigation']['IRRIG_FULL']
        irrig_partial           = config['irrigation']['IRRIG_PARTIAL']
        maker_ch_addr           = config['maker_channel']['MAKER_CH_ADDR']
        maker_ch_key            = config['maker_channel']['MAKER_CH_KEY']

        
    except Exception, e:
        logger.error('Unable to load config data ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()


    #-----------------------------------------------------------------------
    # CALCULATE WATER DEPTH
    #-----------------------------------------------------------------------      
    try:

        #-----------------------------------------------------------------------
        # Grab weather prediction data from online
        #----------------------------------------------------------------------- 
        web_forecast = get_forecast()
        date_first   = [int(web_forecast['forecast']['simpleforecast']['forecastday'][0]['date']['year']), 
                        int(web_forecast['forecast']['simpleforecast']['forecastday'][0]['date']['month']), 
                        int(web_forecast['forecast']['simpleforecast']['forecastday'][0]['date']['day'])] 


        #-----------------------------------------------------------------------
        # Prepare variables
        #----------------------------------------------------------------------- 
        forecast = {}
        web_temp_low        = [] 
        web_temp_high       = []
        web_precip          = []
        web_precip_chance   = []

        for i in range(0, len(web_forecast['forecast']['simpleforecast']['forecastday'])):
            # date = (86400 * i + date_first) * 1000
            web_temp_low.append(int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['low']['celsius']))
            web_temp_high.append(int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['high']['celsius']))
            web_precip.append(int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['qpf_allday']['mm']))
            web_precip_chance.append(1)
        
        logger.info('High temp {temps}'.format(temps=web_temp_high))
        logger.info('Low temp  {temps}'.format(temps=web_temp_low))
        
        irrigation_amount = 0

        # Convert latitude from degrees to radians
        # radians = degrees * (pi/180)
        lat_rad = location[0] * 0.0174533

        # J is the number of the day in the year between 1 (1 January) and 365 or 366 (31 December)
        j = datetime.datetime.now().timetuple().tm_yday


        #-----------------------------------------------------------------------
        # Calculate current depth if file is present otherwise use estimate
        #----------------------------------------------------------------------- 
        try:
            with open('{fl}/data/irrigation.json'.format(fl= folder_loc), 'r') as f:
                irrig_data = json.load(f)

            if len(sys.argv) > 1:
                if '--irrigated' in sys.argv:
                    print('Plot irrigated')
                    irrigation_amount = irrig_data['irrig_amount'][0]
                    logger.info('User request update')

            previous_depth = irrig_data['depth'][0]

            logger.info('previous_depth = {value}'.format(value= previous_depth))
            
            # Fetch previous values from rrd
            actual_temp_mean   = rrd.fetch_list('AVERAGE', 'outside_temp', days= 2)
            actual_precip      = rrd.fetch_list('MAX', 'precip_acc', days= 2)

            logger.info('actual_temp_mean = {value}'.format(value= actual_temp_mean))
            logger.info('actual_precip = {value}'.format(value= actual_precip))

            # Calculate Extraterrestrial radiation for daily periods (Ra)
            ra = ra_calc(j-1, lat_rad)

            # Convert Ra [MJ/m^2/day] to Re [J/m^2/day]
            eto  = eto_tbase_calc(ra* 1000000, actual_temp_mean[-1])
            etc  = eto * kc
            pe   = effective_rainfall_calc(actual_precip[-1])

            current_depth = previous_depth - etc + pe + irrigation_amount

            taw, raw = readily_available_water_calc(soil_type, root_depth, etc)

            if current_depth > raw:
                deep_perculation = current_depth - raw
                current_depth = raw


            logger.info('Water level file found.')
            logger.info('Current depth = {value}'.format(value= current_depth)) 
       
        except Exception, e:
            logger.error('Unable to load irrigation data ({error_v}). Exiting...'.format(
                error_v=e), exc_info=True)
            logger.info('Water level file not found.')
            logger.info('Using 24 l/m^2 as a starting value.')
            current_depth = 24


        #-----------------------------------------------------------------------
        # Populate predicted depth per day
        #----------------------------------------------------------------------- 
        # Create array for predicted depth with first value the starting depth
        field_capacity      = [current_depth] + [0] * (days-1)
        precip              = [0] * days   
        linear_depth        = [0] * days   
        pe                  = [0] * days
        temp_mean           = [0] * days     
        etc                 = [0] * days
        raw                 = [0] * days
        alarm_levels        = [alarm_level] * days
        irrigation_amount   = [irrigation_amount] + [0] * (days-1)

        for day in range(0, days):
            temp_mean[day]    = (web_temp_high[day] + web_temp_low[day]) / 2
            precip[day]       = web_precip[day] * web_precip_chance[day]

            # Calculate Extraterrestrial radiation for daily periods (Ra)
            ra = ra_calc(j + day, lat_rad)

            # Convert Ra [MJ/m^2/day] to Re [J/m^2/day]
            eto     = eto_tbase_calc(ra* 1000000, temp_mean[day])
            etc[day]  = eto * kc
            pe[day]   = effective_rainfall_calc(precip[day])

            # Calculate and limit due to deep perculation
            taw, raw[day] = readily_available_water_calc(soil_type, root_depth, etc[day])
            
            # Estimate next day's depth
            if day + 1 < days:
                field_capacity[day+1] = field_capacity[day] - etc[day] + pe[day]

                if field_capacity[day+1] > raw[day]:
                    field_capacity[day+1] = raw[day]


        logger.info('Water depth = {value}'.format(value= field_capacity))
        logger.info('Effective precip = {value}'.format(value= pe))


        #-----------------------------------------------------------------------
        # Get linear regression for depth
        #-----------------------------------------------------------------------
        m,c = linear_regression([i for i in range(0,days)], field_capacity)

        linear_depth = [m*x+c for x in range(0, days)] 

        logger.info('Linear depth = {value}'.format(value= linear_depth))


        #-----------------------------------------------------------------------
        # Write water level data file
        #----------------------------------------------------------------------- 
        forecast = {
            'date':             date_first,
            'depth':            field_capacity,
            'linear':           linear_depth,
            'precip':           pe,
            'temp':             temp_mean,
            'etc':              etc,
            'raw':              raw,
            'alarm_level':      alarm_levels,
            'irrig_amount':     irrigation_amount
        }

        with open('{fl}/data/irrigation.json'.format(fl= folder_loc), 'w') as f:
            json.dump(forecast, f)


        #-----------------------------------------------------------------------
        # Trigger warning if irrigation is needed
        #-----------------------------------------------------------------------
        if field_capacity[3] <= alarm_level:
            mc = maker_ch.MakerChannel(maker_ch_addr, maker_ch_key, 'WS_water_alarm')
            mc.trigger_an_event()


        logger.info('--- Script Finished ---')


    except Exception, e:
        logger.error('Error ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()

    
#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
