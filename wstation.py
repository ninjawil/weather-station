#-------------------------------------------------------------------------------
#
# Controls shed weather station
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

#!usr/bin/env python

#===============================================================================
# Import modules
#===============================================================================
import sys
import threading
import time
import datetime
import pigpio
import DHT22
import DS18B20
import thingspeak


#===============================================================================
# LOAD DRIVERS
#===============================================================================
pi = pigpio.pi()


#===============================================================================
# GLOBAL VARIABLES
#===============================================================================

# --- Set up GPIO referencing----
GLOBAL_BROADCOM_REF     = True

if GLOBAL_BROADCOM_REF:
    GLOBAL_Pin_11   = 17
    GLOBAL_Pin_12   = 18
    GLOBAL_Pin_13   = 27
    GLOBAL_Pin_14   = 27
else:
    GLOBAL_Pin_11   = 11
    GLOBAL_Pin_12   = 12
    GLOBAL_Pin_13   = 13
    GLOBAL_Pin_14   = 14

# --- System set up ---
GLOBAL_update_rate          = 5 # seconds
GLOBAL_w1_device_path       = '/sys/bus/w1/devices/'

# --- Set up thingspeak ----
GLOBAL_thingspeak_host_addr         = 'api.thingspeak.com:80'
GLOBAL_thingspeak_api_key_filename  = 'thingspeak.txt'
GLOBAL_thingspeak_write_api_key     = ''

# --- Set up sensors ----
GLOBAL_out_temp_sensor_ref  = '28-0414705bceff'
GLOBAL_out_temp_TS_field    = 1

GLOBAL_in_sensor_ref        = 'DHT22'
GLOBAL_in_sensor_pin        = GLOBAL_Pin_11
GLOBAL_in_temp_TS_field     = 2
GLOBAL_in_hum_TS_field      = 3

GLOBAL_door_sensor_pin      = GLOBAL_Pin_14
GLOBAL_door_TS_field        = 4

GLOBAL_rain_sensor_pin      = GLOBAL_Pin_13
GLOBAL_rain_TS_field        = 5
GLOBAL_rain_tick_measure    = 1.5 #millimeters
GLOBAL_rain_tick_meas_time  = 0.5 #minutes
GLOBAL_rain_tick_count      = 0
GLOBAL_rain_task_count      = 0

# --- Set up flashing LED ----
GLOBAL_LED_pin              = GLOBAL_Pin_12
GLOBAL_LED_flash_rate       = 1  # seconds
GLOBAL_next_call            = time.time()

DEBOUNCE_MICROS = 0.5 #seconds
last_rising_edge = None

#===============================================================================
# EDGE CALLBACK FUNCTION TO COUNT RAIN TICKS
#===============================================================================
def count_rain_ticks(gpio, level, tick):
    
    global GLOBAL_rain_tick_count
    global last_rising_edge
    
    pulse = False
    
    if last_rising_edge is not None:
        if pigpio.tickDiff(last_rising_edge, tick) > DEBOUNCE_MICROS:
            pulse = True
    else:
        pulse = True

   if pulse:
        last_rising_edge = tick  
        GLOBAL_rain_tick_count += 1
        print(GLOBAL_rain_tick_count)  
  
 
#===============================================================================
# OUTPUT DATA TO SCREEN
#===============================================================================
def output_data(sensors, data):

    #Check passed data is correct
    if len(sensors) <= len(data):

        print('')

        #Print date and time
        print(datetime.datetime.now())

        field = 0

        # Display each sensor data
        for i in sensors:

            #Check for unit
            if 'temp' in i:
                unit = u'\u00b0C'
            elif 'hum' in i:
                unit = '%'
            else:
                unit = ''

            #Print sensor data
            print(i+'\t'+str(data[field])+unit)

            #Next data field
            field += 1


#===============================================================================
# DOOR SENSOR
#===============================================================================
def get_door_status(door_sensor_pin):
            
    return pi.read(door_sensor_pin)
    

#===============================================================================
# TOGGLE LED
#===============================================================================
def toggle_LED():

    global GLOBAL_next_call
    global GLOBAL_LED_display_time

    if GLOBAL_LED_display_time:
        print(datetime.datetime.now())

    #Prepare next thread time
    GLOBAL_next_call = GLOBAL_next_call + GLOBAL_LED_flash_rate
    threading.Timer( GLOBAL_next_call - time.time(), toggle_LED ).start()

    #Toggle LED
    if pi.read(GLOBAL_LED_pin) == 0:
        pi.write(GLOBAL_LED_pin, 1)
    else:
        pi.write(GLOBAL_LED_pin, 0)


#===============================================================================
# MAIN
#===============================================================================
def main():

    global GLOBAL_in_sensor_ref
    global GLOBAL_in_hum_sensor_enable
    global GLOBAL_rain_tick_count
    global GLOBAL_rain_tick_meas_time
    global GLOBAL_update_rate

    #Set initial variable values
    rain_sensor_enable = True
    out_sensor_enable = True
    in_sensor_enable = True
    thingspeak_enable_update = True
    GLOBAL_LED_display_time = False
    screen_output = False

    #Check and action passed arguments
    if len(sys.argv) > 1:
        if '--outsensor=OFF' in sys.argv:
            out_sensor_enable = False

        if '--insensor=OFF' in sys.argv:
            in_sensor_enable = False

        if '--rainsensor=OFF' in sys.argv:
            rain_sensor_enable = False

        if '--thingspeak=OFF' in sys.argv:
            thingspeak_enable_update = False

        if '--LEDtime=ON' in sys.argv:
            GLOBAL_LED_display_time = True

        if '--display=ON' in sys.argv:
            screen_output = True

        if '--help' in sys.argv:
            print('usage: ./wstation.py {command}')
            print('')
            print('   --outsensor=OFF    ',
                  '- disables outside temperature monitoring')
            print('   --insensor=OFF     ',
                  '- disables inside temperature monitoring')
            print('   --rainsensor=OFF   ',
                  '- disables rainfall monitoring')
            print('   --thingspeak=OFF   ',
                  '- disable update to ThingSpeak')
            print('   --LEDtime=ON       ',
                  '- enables printing of LED toggle time')
            print('   --display=ON       ',
                  '- outputs data to screen')
            sys.exit(0)

    #Set up inside temp and humidity sensor
    DHT22_sensor = DHT22.sensor(pi, GLOBAL_in_sensor_pin)

    #Set up rain sensor input pin
    pi.set_mode(GLOBAL_rain_sensor_pin, pigpio.INPUT)
    rain_gauge = pi.callback(GLOBAL_rain_sensor_pin, 
                             pigpio.RISING_EDGE, 
                             count_rain_ticks)

    #Set up door sensor input pin
    pi.set_mode(GLOBAL_door_sensor_pin, pigpio.INPUT)
    
    #Set up LED flashing thread
    pi.set_mode(GLOBAL_LED_pin, pigpio.OUTPUT)
    timerThread = threading.Thread(target=toggle_LED)
    timerThread.daemon = True
    timerThread.start()
    
    #Read thingspeak write api key from file
    if thingspeak_enable_update:
        GLOBAL_thingspeak_write_api_key = thingspeak.get_write_api_key(
                                            GLOBAL_thingspeak_api_key_filename)
    
    #convert from minutes to no. of tasks
    GLOBAL_rain_tick_meas_time = (GLOBAL_rain_tick_meas_time * 60) / GLOBAL_update_rate
    GLOBAL_rain_tick_count = 0
    GLOBAL_rain_task_count = 0
    
    #Prepare variables
    sensor_data     = []
    sensors         = []
    
    DEBOUNCE_MICROS = 1000000 * DEBOUNCE_MICROS # convert from seconds to microseconds

    #Prepare sensor list
    if out_sensor_enable:
        sensors.append('outside temp')
    if in_sensor_enable:
        sensors.append('inside temp')
        sensors.append('inside hum')
    if door_sensor_enable:
        sensors.append('door open')
    if rain_sensor_enable:
        sensors.append('rainfall')

    #Prepare thingspeak data to match sensor number
    sensor_data = [0 for i in sensors]

    if thingspeak_enable_update and screen_output:
        print('Thingspeak set up:')
        print(sensors)
        print(sensor_data)

    next_reading = time.time()

    #Main code
    try:
        while True:
            
            #Get rain fall measurement
            if out_sensor_enable:
                if GLOBAL_rain_task_count == GLOBAL_rain_tick_meas_time:
                    sensor_data[GLOBAL_rain_TS_field-1] = GLOBAL_rain_tick_count * GLOBAL_rain_tick_measure
                    GLOBAL_rain_tick_count = 0
                    GLOBAL_rain_task_count = 0
                else:
                    GLOBAL_rain_task_count += 1
                    print(GLOBAL_rain_task_count)

            #Check door status
            if door_sensor_enable:
                sensor_data[GLOBAL_door_TS_field-1] = get_door_status(GLOBAL_door_sensor_pin)
                
            #Get outside temperature
            if out_sensor_enable:
                sensor_data[GLOBAL_out_temp_TS_field-1] = DS18B20.get_temp(
                                                            GLOBAL_w1_device_path, 
                                                            GLOBAL_out_temp_sensor_ref)
                
            #Get inside temperature and humidity
            if in_sensor_enable:
                DHT22_sensor.trigger()
                time.sleep(0.2)  #Do not over poll DHT22
                sensor_data[GLOBAL_in_temp_TS_field-1] = DHT22_sensor.temperature()
                sensor_data[GLOBAL_in_hum_TS_field-1] = DHT22_sensor.humidity()

            #Display data on screen
            if screen_output:
                output_data(sensors, sensor_data)

            #Send data to thingspeak
            if thingspeak_enable_update:
                thingspeak.update_channel(GLOBAL_thingspeak_host_addr, 
                                          GLOBAL_thingspeak_write_api_key, 
                                          sensor_data, screen_output)

            #Delay to give update rate
            next_reading += GLOBAL_update_rate
            sleep_length = next_reading - time.time()
            #print(sleep_length)
            if sleep_length > 0:
                time.sleep(sleep_length)


    except KeyboardInterrupt:
        
        print('\nExiting program...')
        
        #Set pins to OFF state
        pi.write(GLOBAL_LED_pin, 0)

        #Stop processes
        DHT22_sensor.cancel()
        rain_gauge.cancel()
        
        sys.exit(0)


#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
