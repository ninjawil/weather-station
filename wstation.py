#-------------------------------------------------------------------------------
#
# 'Controls shed weather station
#
# The MIT License (MIT)
#
# Copyright (c) 2015 William De Freitas
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#-------------------------------------------------------------------------------

#!/usr/bin/env python

'''Gathers data from various sensors to capture weather conditiona and take
apropriate actions in shed.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import threading
import time
import datetime
import logging

# Third party modules
import rrdtool
import pigpio
import DHT22

# Application modules
import DS18B20
import thingspeak
import screen_op
import settings as s




#===============================================================================
# SET UP logger
#===============================================================================
logging.basicConfig(filename=s.LOG_FILENAME, level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.info('--- Wstation Started ---')


#===============================================================================
# LOAD DRIVERS
#===============================================================================
pi = pigpio.pi()


#===============================================================================
# GLOBAL VARIABLES
#===============================================================================
led_thread_next_call     = time.time()
rain_thread_next_call    = time.time()
last_rising_edge = None


#===============================================================================
# EDGE CALLBACK FUNCTION TO COUNT RAIN TICKS
#===============================================================================
def count_rain_ticks(gpio, level, tick):
    
    '''Count the ticks from a reed switch'''
    
    global precip_tick_count
    global last_rising_edge
    
    pulse = False
    
    if last_rising_edge is not None:
        #check tick in microseconds
        if pigpio.tickDiff(last_rising_edge, tick) > s.DEBOUNCE_MICROS * 1000000:
            pulse = True

    else:
        pulse = True

    if pulse:
        last_rising_edge = tick  
        precip_tick_count += 1
        
    logger.info('Rain tick pulse = %s', pulse)

   
#===============================================================================
# TOGGLE LED
#===============================================================================
def toggle_LED():
    
    '''A thread called at a specific time to toggle an LED on/off'''

    global led_thread_next_call

    #Prepare next thread time
    led_thread_next_call = led_thread_next_call + s.LED_FLASH_RATE
    threading.Timer(led_thread_next_call-time.time(), toggle_LED).start()

    #Toggle LED
    pi.write(s.LED_PIN, not(pi.read(s.LED_PIN)))

  
#===============================================================================
# TOGGLE LED
#===============================================================================
def create_rrd_data_source(source_name, source_type, source_heartbeat, 
                            source_min, source_max):
    return 'DS:{ds_name}:{ds_type}:{ds_hb}:{ds_min}:{ds_max}'.format(
        ds_name=source_name.replace(' ','_'),
        ds_type=source_type,
        ds_hb=source_heartbeat,
        ds_min=source_min,
        ds_max=source_max)

    

#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    global precip_tick_count
    global precip_accu
    global rain_thread_next_call

    #Set initial variable values
    rain_sensor_enable           = True
    out_sensor_enable            = True
    in_sensor_enable             = True
    thingspeak_enable_update     = True
    screen_output                = True
    door_sensor_enable           = True
    rrdtool_enable_update        = True
    
    sensors                      = {}
    rrd_data_sources             = []
    rrd_set                      = []
    rows                         = 0

    #---------------------------------------------------------------------------
    # CHECK AND ACTION PASSED ARGUMENTS
    #---------------------------------------------------------------------------
    if len(sys.argv) > 1:
        if '--outsensor=OFF' in sys.argv:
            out_sensor_enable = False
        if '--insensor=OFF' in sys.argv:
            in_sensor_enable = False
        if '--rainsensor=OFF' in sys.argv:
            rain_sensor_enable = False
        if '--rrdtool=OFF' in sys.argv:
            rrdtool_enable_update = False
        if '--thingspeak=OFF' in sys.argv:
            thingspeak_enable_update = False
        if '--quiet' in sys.argv:
            screen_output = False 
        if '--help' in sys.argv:
            screen_op.help_menu()
            sys.exit(0)


    #---------------------------------------------------------------------------
    # SET UP LED HARDWARE AND THREAD
    #---------------------------------------------------------------------------
    pi.set_mode(s.LED_PIN, pigpio.OUTPUT)
    ledThread = threading.Thread(target=toggle_LED)
    ledThread.daemon = True
    ledThread.start()

    
    #---------------------------------------------------------------------------
    # SET UP OUTSIDE TEMPERATURE SENSOR
    #---------------------------------------------------------------------------
    if out_sensor_enable:
        #Add to sensor list
        sensors[s.OUT_TEMP_NAME] = [s.OUT_TEMP_TS_FIELD, s.OUT_TEMP_UNIT, 0]
        
        #Prepare RRD data sources
        if rrdtool_enable_update:
            rrd_data_sources += [create_rrd_data_source(s.OUT_TEMP_NAME, 
                                    s.OUT_TEMP_TYPE,
                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                    str(s.OUT_TEMP_MIN),
                                    str(s.OUT_TEMP_MAX))]


    #---------------------------------------------------------------------------
    # SET UP INSIDE TEMPERATURE SENSOR
    #---------------------------------------------------------------------------
    if in_sensor_enable:
        #Add to sensor list
        sensors[s.IN_TEMP_NAME] = [s.IN_TEMP_TS_FIELD, s.IN_TEMP_UNIT, 0]
        sensors[s.IN_HUM_NAME] = [s.IN_HUM_TS_FIELD, s.IN_HUM_UNIT, 0]
        
        #Set up hardware
        DHT22_sensor = DHT22.sensor(pi, s.IN_SENSOR_PIN)
        
        #Prepare RRD data sources
        if rrdtool_enable_update:
            rrd_data_sources += [create_rrd_data_source(s.IN_TEMP_NAME, 
                                    s.IN_TEMP_TYPE,
                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                    str(s.IN_TEMP_MIN),
                                    str(s.IN_TEMP_MAX))]
            rrd_data_sources += [create_rrd_data_source(s.IN_HUM_NAME, 
                                    s.IN_HUM_TYPE,
                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                    str(s.IN_HUM_MIN),
                                    str(s.IN_HUM_MAX))]

    
    #---------------------------------------------------------------------------
    # SET UP DOOR SENSOR
    #---------------------------------------------------------------------------
    if door_sensor_enable:
        #Add to sensor list
        sensors[s.DOOR_NAME] = [s.DOOR_TS_FIELD, s.DOOR_UNIT, 0]
        
        #Set up hardware
        pi.set_mode(s.DOOR_SENSOR_PIN, pigpio.INPUT)
        
        #Prepare RRD data sources
        if rrdtool_enable_update:
            rrd_data_sources += [create_rrd_data_source(s.DOOR_NAME, 
                                    s.DOOR_TYPE,
                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                    str(s.DOOR_MIN),
                                    str(s.DOOR_MAX))]


    #---------------------------------------------------------------------------
    # SET UP RAIN SENSOR
    #---------------------------------------------------------------------------
    if rain_sensor_enable:
        #Set up inital values for variables
        precip_tick_count = 0
        precip_accu       = 0
        last_data_values  = []
        
        #Add to sensor list
        sensors[s.PRECIP_RATE_NAME] = [s.PRECIP_RATE_TS_FIELD, s.PRECIP_RATE_UNIT, 0]
        sensors[s.PRECIP_ACCU_NAME] = [s.PRECIP_ACCU_TS_FIELD, s.PRECIP_ACCU_UNIT, 0]
        
        #Set up rain gauge hardware
        pi.set_mode(s.PRECIP_SENSOR_PIN, pigpio.INPUT)
        rain_gauge = pi.callback(s.PRECIP_SENSOR_PIN, pigpio.FALLING_EDGE, 
                                    count_rain_ticks)
        
        #Prepare RRD data sources
        if rrdtool_enable_update:
            rrd_data_sources += [create_rrd_data_source(s.PRECIP_RATE_NAME, 
                                    s.PRECIP_RATE_TYPE,
                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                    str(s.PRECIP_RATE_MIN),
                                    str(s.PRECIP_RATE_MAX))]
            rrd_data_sources += [create_rrd_data_source(s.PRECIP_ACCU_NAME, 
                                    s.PRECIP_ACCU_TYPE,
                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                    str(s.PRECIP_ACCU_MIN),
                                    str(s.PRECIP_ACCU_MAX))]                               


    #---------------------------------------------------------------------------
    # SET THINGSPEAK ACCOUNT
    #---------------------------------------------------------------------------
    if thingspeak_enable_update:
        #Set up inital values for variables
        thingspeak_write_api_key     = ''
        
        #Set up thingspeak account
        ts_acc = thingspeak.TSChannel(s.THINGSPEAK_HOST_ADDR,
                                        file=s.THINGSPEAK_API_KEY_FILENAME,
                                        ch_id=s.THINGSPEAK_CHANNEL_ID) 


    #---------------------------------------------------------------------------
    # SET NEXT LOOP TIME
    #---------------------------------------------------------------------------
    next_reading = time.time() + s.UPDATE_RATE
    
    
    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    if rrdtool_enable_update:
        #Set up inital values for variables
        rra_files        = []
  
        #Prepare RRA files
        for i in range(0,len(s.RRDTOOL_RRA),3):
            rra_files.append('RRA:{cf}:0.5:{steps}:{rows}'.format(
                cf=s.RRDTOOL_RRA[i],
                steps=str((s.RRDTOOL_RRA[i+1]*60)/s.UPDATE_RATE),
                rows=str(((s.RRDTOOL_RRA[i+2])*24*60)/s.RRDTOOL_RRA[i+1])))
 
        #Prepare RRD set
        rrd_set = [s.RRDTOOL_RRD_FILE, 
                    '--step', '{step}'.format(step=s.UPDATE_RATE), 
                    '--start', '{start_time:.0f}'.format(start_time=next_reading)]
        rrd_set +=  rrd_data_sources + rra_files
        
        #Create RRD files if none exist
        if not os.path.exists(s.RRDTOOL_RRD_FILE):
            logger.info('RRD file not found')
            logger.info(rrd_set)
            rrdtool.create(rrd_set)
            logger.info('New RRD file created')
        else:
            #Fetch data from round robin database & extract next entry time to sync loop
            logger.info('RRD file found')
            data_values = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                        '-s', str(s.UPDATE_RATE * -2))
            next_reading  = data_values[0][1]
            logger.info('RRD FETCH: Next sensor reading at {time}'.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))


    #---------------------------------------------------------------------------
    # TIMED LOOP
    #---------------------------------------------------------------------------
    try:
        while True:
            
            #-------------------------------------------------------------------
            # Print loop start time
            #-------------------------------------------------------------------
            if screen_output:
                rows -= 1
                if rows <= 0:
                    rows = screen_op.draw_screen(sensors,
                                                    thingspeak_enable_update, 
                                                    ts_acc.api_key,
                                                    rrdtool_enable_update,
                                                    rrd_set)
                print(time.strftime('%Y-%m-%d\t%H:%M:%S', time.gmtime(next_reading))),


            #-------------------------------------------------------------------
            # Delay to give update rate
            #-------------------------------------------------------------------
            sleep_length = next_reading - time.time()
            if sleep_length > 0:
                time.sleep(sleep_length)


            #-------------------------------------------------------------------
            # Get loop start time
            #-------------------------------------------------------------------
            loop_start_time = datetime.datetime.now()
            logger.info('Loop start time: {start_time}'.format(
                start_time=loop_start_time.strftime('%Y-%m-%d %H:%M:%S')))


            #-------------------------------------------------------------------
            # Get rain fall measurement
            #-------------------------------------------------------------------
            if rain_sensor_enable:
                
                #Calculate precip rate and reset it
                sensors[s.PRECIP_RATE_NAME][s.VALUE] = precip_tick_count * s.PRECIP_TICK_MEASURE
                precip_tick_count = 0.000000
                logger.info('Pricipitation counter RESET')
   
                #Get previous precip acc'ed value
                if rrdtool_enable_update:
                    data_values = []
                    last_precip_accu = None
                    tuple_location = 0
                    
                    #Fetch data from round robin database
                    data_values = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                                '-s', str(s.UPDATE_RATE * -2))

                    #Sync task time to rrd database
                    next_reading  = data_values[0][1]
                    logger.info('Next sensor reading at {time}'.format(
                        time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))
                    
                    #Extract time and precip acc value from fetched tuple
                    data_location = data_values[1].index(s.PRECIP_ACCU_NAME.replace(' ','_'))
                    while last_precip_accu is None and -tuple_location < len(data_values[2]):
                        tuple_location -= 1
                        last_precip_accu = data_values[2][tuple_location][data_location]
                        
                    last_entry_time = data_values[0][1] + (tuple_location * s.UPDATE_RATE)
                    
                    #If no data present, set it to 0
                    if last_precip_accu is None:
                        last_precip_accu = 0.00
                        
                #Get value from thingspeak if rrdtool is disabled
                elif thingspeak_enable_update:
                    last_data_values = ts_acc.get_last_feed_entry()
                    last_entry_time = last_data_values["created at"]
                    last_precip_accu = last_data_values["field"+str(s.PRECIP_ACCU_TS_FIELD)]
   
                #Previous reset time
                last_reset = loop_start_time.replace(hour=s.PRECIP_ACC_RESET_TIME[0], 
                                                        minute=s.PRECIP_ACC_RESET_TIME[1], 
                                                        second=s.PRECIP_ACC_RESET_TIME[2], 
                                                        microsecond=s.PRECIP_ACC_RESET_TIME[3])
    
                #Reset precip acc    
                time_since_last_reset = (loop_start_time - last_reset).total_seconds()
                time_since_last_feed_entry = time.mktime(loop_start_time.timetuple()) - last_entry_time
                if time_since_last_feed_entry > time_since_last_reset:
                    sensors[s.PRECIP_ACCU_NAME][s.VALUE] = 0.00
                    logger.info('Pricipitation accumulated RESET')
                else:
                    sensors[s.PRECIP_ACCU_NAME][s.VALUE] = last_precip_accu
                
                #Add previous precip. acc'ed value to current precip. rate
                sensors[s.PRECIP_ACCU_NAME][s.VALUE] += sensors[s.PRECIP_RATE_NAME][s.VALUE]
                
            else:
                # If rrdtool is disable just increment task time by rate
                next_reading += s.UPDATE_RATE
                logger.info('Next sensor reading at  {time}'.format(
                    time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))


            #-------------------------------------------------------------------
            # Check door status
            #-------------------------------------------------------------------
            if door_sensor_enable:
                logger.info('Reading value from door sensor')
                sensors[s.DOOR_NAME][s.VALUE] = pi.read(s.DOOR_SENSOR_PIN)


            #-------------------------------------------------------------------
            # Get outside temperature
            #-------------------------------------------------------------------
            if out_sensor_enable:
                logger.info('Reading value from DS18B20 sensor')
                sensors[s.OUT_TEMP_NAME][s.VALUE] = DS18B20.get_temp(
                                                            s.W1_DEVICE_PATH, 
                                                            s.OUT_TEMP_SENSOR_REF)

   
            #-------------------------------------------------------------------
            # Get inside temperature and humidity
            #-------------------------------------------------------------------
            if in_sensor_enable:
                logger.info('Reading value from DHT22 sensor')
                DHT22_sensor.trigger()
                time.sleep(0.2)  #Do not over poll DHT22
                sensors[s.IN_TEMP_NAME][s.VALUE] = DHT22_sensor.temperature()
                sensors[s.IN_HUM_NAME][s.VALUE]  = DHT22_sensor.humidity()

   
            #-------------------------------------------------------------------
            # Display data on screen
            #-------------------------------------------------------------------
            if screen_output:
                for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
                    if key == s.DOOR_NAME:
                        if value[s.VALUE]:
                            print('\tOPEN\t'),
                        else:
                            print('\tCLOSED\t'),
                    else:
                        print('\t{value:2.2f}{unit} '.format(value=value[s.VALUE],
                                                             unit=value[s.UNIT])),

  
            #-------------------------------------------------------------------
            # Send data to thingspeak
            #-------------------------------------------------------------------
            if thingspeak_enable_update:
                #Create dictionary with field as key and value
                sensor_data = {}
                for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
                    sensor_data['field'+str(value[s.TS_FIELD])] = value[s.VALUE]
                response = ts_acc.update_channel(sensor_data)
                logger.info('Thingspeak response: {code} - {reason}'.format(
                                code=response.status_code, 
                                reason=response.reason))
                if screen_output:
                    print('\t{response}'.format(response=response.reason)),
            elif screen_output:
                print('\tN/A'),

   
            #-------------------------------------------------------------------
            # Add data to RRD
            #-------------------------------------------------------------------
            if rrdtool_enable_update:
                logger.info('Updating RRD file')
                sensor_data = []
                for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
                    sensor_data.append(value[s.VALUE])
                sensor_data = [str(i) for i in sensor_data]
                rrdtool.update(s.RRDTOOL_RRD_FILE, 'N:' + ':'.join(sensor_data))
                if screen_output:
                    print('\t\tOK')
            elif screen_output:
                print('\t\tN/A')


    #---------------------------------------------------------------------------
    # User exit command
    #---------------------------------------------------------------------------
    except KeyboardInterrupt:

        logger.info('USER ACTION: End command')
        
        if screen_output:
            print('\nExiting program...')
        
        #Set pins to OFF state
        pi.write(s.LED_PIN, 0)

        #Stop processes
        DHT22_sensor.cancel()
        rain_gauge.cancel()
        
        logger.info('--- Finished ---')
        

#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
