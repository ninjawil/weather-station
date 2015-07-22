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
import settings


#===============================================================================
# LOAD DRIVERS
#===============================================================================
pi = pigpio.pi()


#===============================================================================
# GLOBAL VARIABLES
#===============================================================================

RAIN_TICK_MEASURE    = 1.5 #millimeters
RAIN_TICK_MEAS_TIME  = 0.05 #minutes
rain_tick_count      = 0
rain_task_count      = 0

led_thread_next_call     = time.time()

DEBOUNCE_MICROS = 0.5 #seconds
last_rising_edge = None


#===============================================================================
# EDGE CALLBACK FUNCTION TO COUNT RAIN TICKS
#===============================================================================
def count_rain_ticks(gpio, level, tick):
    
    global rain_tick_count
    global last_rising_edge
    
    pulse = False
    
    if last_rising_edge is not None:
        if pigpio.tickDiff(last_rising_edge, tick) > DEBOUNCE_MICROS:
            pulse = True
    else:
        pulse = True

    if pulse:
        last_rising_edge = tick  
        rain_tick_count += 1
        print(rain_tick_count)  
  
 
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
def get_door_status(sensor_pin):
    return pi.read(sensor_pin)
    

#===============================================================================
# TOGGLE LED
#===============================================================================
def toggle_LED():

    global led_thread_next_call
    global led_display_time

    if led_display_time:
        print(datetime.datetime.now())

    #Prepare next thread time
    led_thread_next_call = led_thread_next_call + settings.LED_FLASH_RATE
    threading.Timer( led_thread_next_call - time.time(), toggle_LED ).start()

    #Toggle LED
    if pi.read(settings.LED_PIN) == 0:
        pi.write(settings.LED_PIN, 1)
    else:
        pi.write(settings.LED_PIN, 0)


#===============================================================================
# MAIN
#===============================================================================
def main():

    global RAIN_TICK_MEAS_TIME
    global DEBOUNCE_MICROS
    
    global led_display_time
    global rain_tick_count


    #Set initial variable values
    rain_sensor_enable           = True
    out_sensor_enable            = True
    in_sensor_enable             = True
    thingspeak_enable_update     = True
    led_display_time             = False
    screen_output                = False
    door_sensor_enable           = True
    
    thingspeak_write_api_key     = ''
    
    sensor_data                  = []
    sensors                      = []
    
    rain_tick_count       = 0
    rain_task_count       = 0
    
    #convert from seconds to microseconds
    DEBOUNCE_MICROS = 1000000 * DEBOUNCE_MICROS 

    #convert from minutes to no. of tasks
    RAIN_TICK_MEAS_TIME = (RAIN_TICK_MEAS_TIME * 60) / settings.UPDATE_RATE
    
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
            led_display_time = True
            
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

    #Set up pin outs
    pi.set_mode(settings.RAIN_SENSOR_PIN, pigpio.INPUT)
    pi.set_mode(settings.DOOR_SENSOR_PIN, pigpio.INPUT)
    DHT22_sensor = DHT22.sensor(pi, settings.IN_SENSOR_PIN)
    rain_gauge = pi.callback(settings.RAIN_SENSOR_PIN, pigpio.RISING_EDGE, 
                             count_rain_ticks)
    
    #Set up LED flashing thread
    pi.set_mode(settings.LED_PIN, pigpio.OUTPUT)
    timerThread = threading.Thread(target=toggle_LED)
    timerThread.daemon = True
    timerThread.start()
    
    #Read thingspeak write api key from file
    if thingspeak_enable_update:
        thingspeak_write_api_key = thingspeak.get_write_api_key(
                                            settings.THINGSPEAK_API_KEY_FILENAME)

    #Display thingspeak settings
    if thingspeak_enable_update and screen_output:
        print('Thingspeak set up:')
        print(sensors)
        print(sensor_data)

    #Set next loop time
    next_reading = time.time()


    #Main code
    try:
        while True:
            
            #Get rain fall measurement
            if out_sensor_enable:
                if rain_task_count == RAIN_TICK_MEAS_TIME:
                    sensor_data[settings.RAIN_TS_FIELD-1] = rain_tick_count * RAIN_TICK_MEASURE
                    rain_tick_count = 0
                    rain_task_count = 0
                else:
                    rain_task_count += 1
                    print(rain_task_count)

            #Check door status
            if door_sensor_enable:
                sensor_data[settings.DOOR_TS_FIELD-1] = get_door_status(
                                                            settings.DOOR_SENSOR_PIN)
                
            #Get outside temperature
            if out_sensor_enable:
                sensor_data[settings.OUT_TEMP_TS_FIELD-1] = DS18B20.get_temp(
                                                            settings.W1_DEVICE_PATH, 
                                                            settings.OUT_TEMP_SENSOR_REF)
                
            #Get inside temperature and humidity
            if in_sensor_enable:
                DHT22_sensor.trigger()
                time.sleep(0.2)  #Do not over poll DHT22
                sensor_data[settings.IN_TEMP_TS_FIELD-1] = DHT22_sensor.temperature()
                sensor_data[settings.IN_HUM_TS_FIELD-1] = DHT22_sensor.humidity()

            #Display data on screen
            if screen_output:
                output_data(sensors, sensor_data)

            #Send data to thingspeak
            if thingspeak_enable_update:
                thingspeak.update_channel(settings.THINGSPEAK_HOST_ADDR, 
                                          thingspeak_write_api_key, 
                                          sensor_data, screen_output)

            #Delay to give update rate
            next_reading += settings.UPDATE_RATE
            sleep_length = next_reading - time.time()
            #print(sleep_length)
            if sleep_length > 0:
                time.sleep(sleep_length)


    except KeyboardInterrupt:
        
        print('\nExiting program...')
        
        #Set pins to OFF state
        pi.write(settings.LED_PIN, 0)

        #Stop processes
        DHT22_sensor.cancel()
        rain_gauge.cancel()
        
        sys.exit(0)


#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
