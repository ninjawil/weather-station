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
    dr = =1 + 0.033 * math.cos(0.0172 * j)

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
        return (re / (LATENT_HEAT_FLUX * WATER_DENSITY)) * ((temp_mean + 5) / 100)) * 1000
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

        location                = config['irrigation']['COORDINATE']
        alarm_enable            = config['irrigation']['ALARM_ENABLE']
        alarm_level             = config['irrigation']['ALARM_LEVEL']
        net_irrig_depth         = config['irrigation']['NET_IRRIGATION_DEPTH']
        kc                      = config['irrigation']['CROP_FACTOR_KC']
        days                    = config['irrigation']['RECOMMENDED_WATERING_DAYS']
        soil_type               = config['irrigation']['SOIL_TYPE']
        root_depth              = config['irrigation']['ROOT_DEPTH']
        
    except Exception, e:
        logger.error('Unable to load config data. Exiting...')
        sys.exit()


    #-----------------------------------------------------------------------
    # CALCULATE WATER DEPTH
    #-----------------------------------------------------------------------      
    try:

        #-----------------------------------------------------------------------
        # Grab weather prediction data from online
        #----------------------------------------------------------------------- 
        # web_forecast = get_forecast()
        # temp_low   = [int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['high']['celsius'])
        #                             for i in range(0, len(web_forecast['forecast']['simpleforecast']['forecastday'])) ]
        # temp_high  = [int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['low']['celsius'])
        #                             for i in range(0, len(web_forecast['forecast']['simpleforecast']['forecastday'])) ]
        # precip     = [int(web_forecast['forecast']['simpleforecast']['forecastday'][i]['qpf_allday']['mm'])
        #                             for i in range(0, len(web_forecast['forecast']['simpleforecast']['forecastday'])) ]
        
        web_temp_high       = [20, 19, 19, 19, 19, 17, 16, 19, 19, 20]
        web_temp_low        = [10, 9,  9,  9,  9,  7,  6,  9,  9,  10]
        web_precip          = [0, 6, 5, 5, 6, 14, 1, 0, 6, 5]
        web_precip_chance   = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


        #-----------------------------------------------------------------------
        # Prepare variables
        #----------------------------------------------------------------------- 
        irrigation_amount = 0
        forecast = {}

        # Convert latitude from degrees to radians
        # radians = degrees * (pi/180)
        lat_rad = location(0) * 0.0174533

        # J is the number of the day in the year between 1 (1 January) and 365 or 366 (31 December)
        j = datetime.datetime.now().timetuple().tm_yday


        #-----------------------------------------------------------------------
        # Calculate current depth if file is present otherwise use estimate
        #----------------------------------------------------------------------- 
        try:
            with open('{fl}/data/irrigation.json'.format(fl= folder_loc), 'r') as f:
                irrig_data = json.load(f)

            previous_depth = irrig_data['depth'][0]

            # Fetch previous values from rrd
            actual_temp_mean   = rrd.fetch_list('AVG', 'outside_temp')
            actual_precip      = rrd.fetch_list('MAX', 'precip_acc')

            # Calculate Extraterrestrial radiation for daily periods (Ra)
            ra = ra_calc(j-1, lat_rad)

            # Convert Ra [MJ/m^2/day] to Re [J/m^2/day]
            eto  = eto_tbase_calc(ra* 1000000, temp_mean[-1])
            etc  = eto * kc
            pe   = effective_rainfall_calc(precip[-1])

            current_depth = previous_depth - etc + pe + irrig_data['irrig_amount']

            taw, raw = readily_available_water_calc(soil_type, root_depth, etc)

            if current_depth > raw:
                deep_perculation = current_depth - raw
                current_depth = raw


            logger.info('Water level file found. Getting starting')
            logger.info('Current depth = {value}'.format(value= current_depth)) 
       
        except Exception, e:
            logger.info('Water level file not found.')
            logger.info('Using 24 l/m^2 as a starting value.')
            current_depth = 24


        #-----------------------------------------------------------------------
        # Populate predicted depth per day
        #----------------------------------------------------------------------- 
        # Create array for predicted depth with first value the starting depth
        field_capacity = [current_depth] + [0] * days-1

        raw = [0] * days

        for day in range(0, days-1):
            temp_mean[i]    = (web_temp_high[i] - web_temp_low[i]) / 2
            precip[i]       = web_precip[i] * web_precip_chance[i]

            # Calculate Extraterrestrial radiation for daily periods (Ra)
            ra = ra_calc(j + day, lat_rad)

            # Convert Ra [MJ/m^2/day] to Re [J/m^2/day]
            eto     = eto_tbase_calc(ra* 1000000, temp_mean[i])
            etc[i]  = eto * kc
            pe[i]   = effective_rainfall_calc(precip[i])

            # Estimate next day's depth
            field_capacity[i+1] = field_capacity[i] - etc[i] + pe[i]

            # Calculate and limit due to deep perculation
            taw, raw[i] = readily_available_water_calc(soil_type, root_depth, etc[i])

            if field_capacity[i+1] > raw[i]:
                field_capacity[i+1] = raw[i]


        logger.info('Water depth = {value}'.format(value= field_capacity))
        logger.info('Effective precip = {value}'.format(value= pe))


        #-----------------------------------------------------------------------
        # Get linear regression for depth
        #-----------------------------------------------------------------------
        m,c = linear_regression([i for i in range(0,days-1)], field_capacity)

        linear_depth = [m*x+c for x in range(0, days-1)] 

        logger.info('Linear depth = {value}'.format(value= linear_depth))


        #-----------------------------------------------------------------------
        # Write water level data file
        #----------------------------------------------------------------------- 
        forecast = {
            'depth':            field_capacity,
            'linear':           linear_depth,
            'precip':           pe,
            'temp':             temp_mean,
            'etc':              etc,
            'raw':              raw,
            'irrig_amount':     0
        }

        with open('{fl}/data/irrigation.json'.format(fl= folder_loc), 'w') as f:
            json.dump(forecast, f)


        #-----------------------------------------------------------------------
        # Trigger warning if irrigation is needed
        #-----------------------------------------------------------------------
        if field_capacity(3) <= alarm_level:
            mc = maker_ch.MakerChannel(maker_ch_addr, maker_ch_key, 'WS_water_alarm')
            mc.trigger_an_event()


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
