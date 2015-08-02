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
import settings as s
#import rrdtool


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

 
#===============================================================================
# PREPARE RESET TIME
#===============================================================================
def prepare_reset_time(days_to_add):
    
    now = datetime.datetime.now()
    reset_time = now.replace(hour=s.PRECIP_ACC_RESET_TIME[0], 
                                minute=s.PRECIP_ACC_RESET_TIME[1], 
                                second=s.PRECIP_ACC_RESET_TIME[2], 
                                microsecond=s.PRECIP_ACC_RESET_TIME[3])
    reset_time += datetime.timedelta(days=days_to_add)
    
    print('Next precip. acc. reset at '+str(reset_time))
    
    return (reset_time - now).total_seconds()
    

#===============================================================================
# RESET PRECIPITATION ACCUMULATED VARIABLE
#===============================================================================
def reset_rain_acc():

    global rain_thread_next_call
    global precip_accu
    
    print('')
    print('Accumulated Precipitation = 0.0mm')
    
    #Prepare next thread time
    rain_thread_next_call += prepare_reset_time(1)
    threading.Timer(rain_thread_next_call-time.time(), reset_rain_acc).start()

    #reset precipitation accummulated
    precip_accu = 0
   
 
#===============================================================================
# OUTPUT DATA TO SCREEN
#===============================================================================
def output_data(sensors):
    
    print('  Field\tName\t\tValue\tUnit')
    print('  ---------------------------------------')
    for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
        print('  ' + str(value[s.TS_FIELD]) + '\t' + key + 
                '\t' + str(value[s.VALUE]) + '\t' + value[s.UNIT])


#===============================================================================
# TOGGLE LED
#===============================================================================
def toggle_LED():

    global led_thread_next_call

    #Prepare next thread time
    led_thread_next_call = led_thread_next_call + s.LED_FLASH_RATE
    threading.Timer(led_thread_next_call-time.time(), toggle_LED).start()

    #Toggle LED
    pi.write(s.LED_PIN, not(pi.read(s.LED_PIN)))

#===============================================================================
# MAIN
#===============================================================================
def main():

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
    
    thingspeak_write_api_key     = ''
    
    sensors                      = {}
    sensor_data                  = {}
    
    precip_tick_count = 0
    precip_accu       = 0

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
        if '--quiet' in sys.argv:
            screen_output = False 
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
            print('   --quiet            ',
                  '- outputs data to screen')
            sys.exit(0)
  
   #Prepare sensor list
    if out_sensor_enable:
        sensors[s.OUT_TEMP_NAME] = [0,0,0]
        sensors[s.OUT_TEMP_NAME][s.TS_FIELD] = s.OUT_TEMP_TS_FIELD 
        sensors[s.OUT_TEMP_NAME][s.VALUE] = 0
        sensors[s.OUT_TEMP_NAME][s.UNIT] = s.OUT_TEMP_UNIT
                
    if in_sensor_enable:
        sensors[s.IN_TEMP_NAME] = [0,0,0]
        sensors[s.IN_TEMP_NAME][s.TS_FIELD] = s.IN_TEMP_TS_FIELD 
        sensors[s.IN_TEMP_NAME][s.VALUE] = 0
        sensors[s.IN_TEMP_NAME][s.UNIT] = s.IN_TEMP_UNIT
        sensors[s.IN_HUM_NAME] = [0,0,0]
        sensors[s.IN_HUM_NAME][s.TS_FIELD] = s.IN_HUM_TS_FIELD 
        sensors[s.IN_HUM_NAME][s.VALUE] = 0
        sensors[s.IN_HUM_NAME][s.UNIT] = s.IN_HUM_UNIT

    if door_sensor_enable:
        sensors[s.DOOR_NAME] = [0,0,0]
        sensors[s.DOOR_NAME][s.TS_FIELD] = s.DOOR_TS_FIELD 
        sensors[s.DOOR_NAME][s.VALUE] = 0
        sensors[s.DOOR_NAME][s.UNIT] = s.DOOR_UNIT

    if rain_sensor_enable:
        sensors[s.PRECIP_RATE_NAME] = [0,0,0]
        sensors[s.PRECIP_RATE_NAME][s.TS_FIELD] = s.PRECIP_RATE_TS_FIELD 
        sensors[s.PRECIP_RATE_NAME][s.VALUE] = 0
        sensors[s.PRECIP_RATE_NAME][s.UNIT] = s.PRECIP_RATE_UNIT
        sensors[s.PRECIP_ACCU_NAME] = [0,0,0]
        sensors[s.PRECIP_ACCU_NAME][s.TS_FIELD] = s.PRECIP_ACCU_TS_FIELD 
        sensors[s.PRECIP_ACCU_NAME][s.VALUE] = 0
        sensors[s.PRECIP_ACCU_NAME][s.UNIT] = s.PRECIP_ACCU_UNIT                        
 
    #Prepare rrd data
    
    

    #Set up pin outs
    pi.set_mode(s.PRECIP_SENSOR_PIN, pigpio.INPUT)
    pi.set_mode(s.DOOR_SENSOR_PIN, pigpio.INPUT)
    pi.set_mode(s.LED_PIN, pigpio.OUTPUT)
    DHT22_sensor = DHT22.sensor(pi, s.IN_SENSOR_PIN)
    rain_gauge = pi.callback(s.PRECIP_SENSOR_PIN, pigpio.FALLING_EDGE, 
                             count_rain_ticks)
    
    #Set up LED flashing thread
    ledThread = threading.Thread(target=toggle_LED)
    ledThread.daemon = True
    ledThread.start()
    
    #Set up rain acc reset thread and reset precip accumulated variable
    if rain_sensor_enable:
        rain_thread_next_call += prepare_reset_time(0)
        rainThread = threading.Timer(rain_thread_next_call-time.time(), reset_rain_acc)
        rainThread.daemon = True
        rainThread.start()
    
    #Set up thingpseak
    if thingspeak_enable_update:
        thingspeak_acc = thingspeak.ThingspeakAcc(s.THINGSPEAK_HOST_ADDR,
                                                    s.THINGSPEAK_API_KEY_FILENAME)

    #if rrdtool_enable_update:
     #   rrdtool.create(

    #Display thingspeak settings
    if thingspeak_enable_update and screen_output:
        print('\nThingspeak set up:')
        output_data(sensors)

    #Set next loop time
    next_reading = time.time()


    #Main code
    try:
        while True:
            
            #Print loop start time
            if screen_output:
                print('')
                print(datetime.datetime.now())

            #Get rain fall measurement
            if rain_sensor_enable:
                sensors[s.PRECIP_RATE_NAME][s.VALUE] = precip_tick_count * s.PRECIP_TICK_MEASURE
                precip_accu += sensors[s.PRECIP_RATE_NAME][s.VALUE]
                sensors[s.PRECIP_ACCU_NAME][s.VALUE] = precip_accu
                precip_tick_count = 0

            #Check door status
            if door_sensor_enable:
                sensors[s.DOOR_NAME][s.VALUE] = pi.read(s.DOOR_SENSOR_PIN)
                
            #Get outside temperature
            if out_sensor_enable:
                sensors[s.OUT_TEMP_NAME][s.VALUE] = DS18B20.get_temp(
                                                            s.W1_DEVICE_PATH, 
                                                            s.OUT_TEMP_SENSOR_REF)
                
            #Get inside temperature and humidity
            if in_sensor_enable:
                DHT22_sensor.trigger()
                time.sleep(0.2)  #Do not over poll DHT22
                sensors[s.IN_TEMP_NAME][s.VALUE] = DHT22_sensor.temperature()
                sensors[s.IN_HUM_NAME][s.VALUE]  = DHT22_sensor.humidity()
   
            #Send data to thingspeak
            if thingspeak_enable_update:
                for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
                    sensor_data[value[s.TS_FIELD]] = value[s.VALUE]
                response = thingspeak_acc.update_channel(sensor_data)

            #Display data on screen
            if screen_output:
                print('')
                output_data(sensors)
                print('\nData sent to thingspeak: '+ response.reason 
                        + '\t status: ' + str(response.status))

            #Delay to give update rate
            next_reading += s.UPDATE_RATE
            sleep_length = next_reading - time.time()
            if sleep_length > 0:
                time.sleep(sleep_length)


    except KeyboardInterrupt:
        
        if screen_output:
            print('\nExiting program...')
        
        #Set pins to OFF state
        pi.write(s.LED_PIN, 0)

        #Stop processes
        DHT22_sensor.cancel()
        rain_gauge.cancel()
        
        sys.exit(0)


#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
