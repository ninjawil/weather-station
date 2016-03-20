#!/usr/bin/env python

''' Script sets up hardware as long as sensor is enabled.
    Reads the data from the sensor and then updates the RRD file.
    Sensor value is initiated with 'U' which passed to the rrdtool will be 
    recorded as NaN. If reading sensor data fails the value is not updated and
    'U' will remain. 
    The script will not exit on sensor failure only once it finishes or if a RRD
    file is not found or PIGPIO does not load correctly.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import time
import collections

# Third party modules
import pigpio
import DHT22

# Application modules
import log
import DS18B20.DS18B20 as DS18B20
import pyenergenie.ener314rt as ener314rt
import settings as s
import rrd_tools
import check_process
import watchdog as wd



#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

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
    wd_err      = wd.ErrorCode(err_file, '0003')


    #---------------------------------------------------------------------------
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    if check_process.is_running(script_name):
        wd_err.set()
        sys.exit()
  

    #---------------------------------------------------------------------------
    # Load PIGPIO
    #---------------------------------------------------------------------------
    try:
        pi = pigpio.pi()

    except Exception, e:
        logger.error('Failed to connect to PIGPIO ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        wd_err.set()
        sys.exit()


    #---------------------------------------------------------------------------
    # Check Rrd File
    #---------------------------------------------------------------------------
    rrd = rrd_tools.RrdFile('{fd1}/data/{fl}'.format(fd1= folder_loc,
                                                    fl= s.RRDTOOL_RRD_FILE))
        
    if not rrd.check_ds_list_match(list(s.SENSOR_SET.keys())):
        wd_err.set()
        sys.exit()



    #---------------------------------------------------------------------------
    # SET UP SENSOR VARIABLES
    #---------------------------------------------------------------------------  
    sensor_value = {x: 'U' for x in s.SENSOR_SET}

    sensor_settings = collections.namedtuple('sensor_settings',
                                             'enable ref unit min max type')     
    sensor = {k: sensor_settings(*s.SENSOR_SET[k]) for k in s.SENSOR_SET}


    #-------------------------------------------------------------------
    # Get inside temperature and humidity
    #-------------------------------------------------------------------
    if sensor['inside_temp'].enable or sensor['inside_hum'].enable: 
        try:
            DHT22_sensor = DHT22.sensor(pi, sensor['inside_temp'].ref)
            DHT22_sensor.trigger()
            time.sleep(0.2)  #Do not over poll DHT22

            temp = DHT22_sensor.temperature()
            hum = DHT22_sensor.humidity() 

            if temp == -999 or hum == -999:
                logger.warning('Reading value from DHT22 sensor... FAILED')

            else:
                if sensor['inside_temp'].enable:
                    sensor_value['inside_temp'] = temp
                if sensor['inside_hum'].enable: 
                    sensor_value['inside_hum']  = hum 

                logger.info('Reading value from DHT22 sensor... OK')

        except ValueError:
            logger.warning('Failed to read DHT22 ({value_error})'.format(
                value_error=ValueError))
            wd_err.set()
                
        finally:
            DHT22_sensor.cancel()


    #-------------------------------------------------------------------
    # Check door status
    #-------------------------------------------------------------------
    if sensor['door_open'].enable:
        try:
            pi.set_mode(sensor['door_open'].ref, pigpio.INPUT)
            sensor_value['door_open'] = pi.read(sensor['door_open'].ref)
            logger.info('Reading value from door sensor... OK')

        except ValueError:
            logger.warning('Failed to read door sensor ({value_error})'.format(
                value_error=ValueError))
            wd_err.set()


    #-------------------------------------------------------------------
    # Get switch data
    #-------------------------------------------------------------------
    if sensor['sw_status'].enable or sensor['sw_power'].enable:
        try:
            switch = ener314rt.MiPlug()
            switch_data = switch.get_data()
            
            if not switch_data or switch_data['switch'] == 'U' or switch_data['real'] == 'U':
                logger.warning('Reading value from switch data... FAILED')
            else:
                logger.info('Reading value from switch data... OK')
                if sensor['sw_status'].enable:
                    sensor_value['sw_status'] = switch_data['switch']
                if sensor['sw_power'].enable:
                    sensor_value['sw_power']  = switch_data['real']

        except Exception, e:
            logger.warning('Failed to read switch data ({value_error})'.format(
                value_error=e), exc_info=True)
            wd_err.set()
                
        finally:
            switch.close()


    #-------------------------------------------------------------------
    # Get door switch values
    #-------------------------------------------------------------------
    if sensor['door_open'].enable:
        try:
            pi.set_mode(sensor['door_open'].ref, pigpio.INPUT)
            sensor_value['door_open'] = pi.read(sensor['door_open'].ref)
            logger.info('Reading value from door sensor... OK')

        except ValueError:
            logger.warning('Failed to read door sensor ({value_error})'.format(
                value_error=ValueError))
            wd_err.set()


    #-------------------------------------------------------------------
    # Get outside temperature
    #-------------------------------------------------------------------
    if sensor['outside_temp'].enable:
        try:
            out_sensor = DS18B20.DS18B20(sensor['outside_temp'].ref, s.W1_DEVICE_PATH)
            sensor_value['outside_temp'] = out_sensor.get_temp()

            if sensor_value['outside_temp'] > 900:
                logger.warning('Failed to read DS18B20 sensor (temp > 900)')
                sensor_value['outside_temp'] = 'U'
            else:
                logger.info('Reading value from DS18B20 sensor... OK')

        except Exception, e:
            logger.warning('Failed to read DS18B20 ({value_error})'.format(
                value_error=e), exc_info=True)
            wd_err.set()
        

    #-------------------------------------------------------------------
    # Add data to RRD
    #-------------------------------------------------------------------
    logger.debug('Update time = {update_time}'.format(update_time= 'N'))#rrd.next_update()))
    logger.info([v for (k, v) in sorted(sensor_value.items()) if v != 'U'])
    
    result = rrd.update_file(timestamp= 'N',
            ds_name= [k for (k, v) in sorted(sensor_value.items()) if v!='U'],
            values= [v for (k, v) in sorted(sensor_value.items()) if v != 'U'])

    if result == 'OK':
        logger.info('Update RRD file OK')
    else:
        logger.error('Failed to update RRD file ({value_error})'.format(
            value_error=result))
        logger.error(sensor_value)
        wd_err.set()


    #-------------------------------------------------------------------
    # Prepare to end script
    #-------------------------------------------------------------------
    logger.info('--- Read Sensors Finished ---')
    sys.exit()

        

#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())