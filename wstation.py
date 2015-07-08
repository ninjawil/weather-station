#-----------------------------------------------------------------------
#
# Controls weatherstation
#
#-----------------------------------------------------------------------

#!usr/bin/env python

#=======================================================================
# Import modules
#=======================================================================
import os, sys, threading
import time, datetime
import httplib, urllib
import pigpio, DHT22


#=======================================================================
# LOAD DRIVERS
#=======================================================================
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

pi = pigpio.pi()


#=======================================================================
# GLOBAL VARIABLES
#=======================================================================

# --- Set up GPIO referencing----
GLOBAL_BROADCOM_REF     = True

if GLOBAL_BROADCOM_REF == True:
    GLOBAL_Pin_11   = 17
    GLOBAL_Pin_12   = 18
    GLOBAL_Pin_13   = 27
else:
    GLOBAL_Pin_11   = 11
    GLOBAL_Pin_12   = 12
    GLOBAL_Pin_13   = 13


# --- System set up ---
GLOBAL_update_rate          = 3 # seconds
GLOBAL_w1_device_path       = '/sys/bus/w1/devices/'
GLOBAL_screen_output        = False


# --- Set up thingspeak ----
GLOBAL_thingspeak_enable_update     = True
GLOBAL_thingspeak_host_addr         = 'api.thingspeak.com:80'
GLOBAL_thingspeak_write_api_key     = '30SNTCFLNJEI3937'

GLOBAL_thingspeak_field_1   = 1
GLOBAL_thingspeak_field_2   = 2
GLOBAL_thingspeak_field_3   = 3
GLOBAL_thingspeak_field_4   = 4
GLOBAL_thingspeak_field_5   = 5
GLOBAL_thingspeak_field_6   = 6
GLOBAL_thingspeak_field_7   = 7
GLOBAL_thingspeak_field_8   = 8


# --- Set up sensors ----
GLOBAL_out_sensor_enable    = True
GLOBAL_out_temp_sensor_ref  = '28-0414705bceff'
GLOBAL_out_temp_TS_field    = GLOBAL_thingspeak_field_1

GLOBAL_in_sensor_enable     = True
GLOBAL_in_sensor_ref        = 'DHT22'
GLOBAL_in_sensor_pin        = GLOBAL_Pin_11
GLOBAL_in_temp_TS_field     = GLOBAL_thingspeak_field_2
GLOBAL_in_hum_TS_field      = GLOBAL_thingspeak_field_3

GLOBAL_door_sensor_enable   = True
GLOBAL_door_sensor_pin      = GLOBAL_Pin_13
GLOBAL_door_TS_field        = GLOBAL_thingspeak_field_4


# --- Set up flashing LED ----
GLOBAL_LED_display_time     = False
GLOBAL_LED_pin              = GLOBAL_Pin_12
GLOBAL_LED_flash_rate       = 1  # seconds
GLOBAL_next_call            = time.time()



#=======================================================================
# SETUP HARDWARE
#=======================================================================
def setup_hardware():

    #Set up DHT22
    global s
    global GLOBAL_in_sensor_pin
    global GLOBAL_door_sensor_pin

    s = DHT22.sensor(pi, GLOBAL_in_sensor_pin)

    #Set up door sensor input pin
    pi.set_mode(GLOBAL_door_sensor_pin, pigpio.INPUT) #Set up LED pin in
    
    #Set up LED flashing thread
    pi.set_mode(GLOBAL_LED_pin, pigpio.OUTPUT) #Set up LED pin out
    timerThread = threading.Thread(target=toggle_LED)
    timerThread.daemon = True
    timerThread.start()


#=======================================================================
# READ RAW DATA FROM W1 SLAVE
#=======================================================================
def w1_slave_read(device_id):

    device_id = GLOBAL_w1_device_path+device_id+'/w1_slave'

    f=open(device_id,'r')
    lines=f.readlines()
    f.close()

    return lines



#=======================================================================
# READ DATA FROM DS18B20
#=======================================================================
def get_ds18b20_temp(device_id):

    lines = w1_slave_read(device_id)

    #If unsuccessful first read loop until temperature acquired
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        print('Failed to read DS18B20. Trying again...')
        lines = w1_slave_read(device_id)

    temp_output = lines[1].find('t=')

    if temp_output != -1:
        temp_string = lines[1].strip()[temp_output+2:]
        temp_c = float(temp_string) / 1000.0

    return temp_c


#=======================================================================
# READ DATA FROM DHT22
#=======================================================================
def get_dht22_data():

    global s

    s.trigger()

    time.sleep(0.2) #Do not over poll DHT22

    return {'temp':s.temperature(), 'hum':s.humidity()}


#=======================================================================
# OUTPUT DATA TO SCREEN
#=======================================================================
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



#=======================================================================
# UPDATE THINGSPEAK CHANNEL
#=======================================================================
def thingspeak_update_channel(channel, field_data):
    
    global GLOBAL_screen_output

    #Create POST data
    data_to_send = {}
    data_to_send['key'] = channel
    for i in range(0, len(field_data)):
        data_to_send['field'+str(i+1)] = field_data[i]

    params = urllib.urlencode(data_to_send)
    headers = {'Content-type': 'application/x-www-form-urlencoded','Accept': 'text/plain'}

    conn = httplib.HTTPConnection(GLOBAL_thingspeak_host_addr)
    conn.request('POST', '/update', params, headers)
    response = conn.getresponse()
    
    if GLOBAL_screen_output == True:
        print('Data sent to thingspeak: ' + response.reason + '\t status: ' + str(response.status))
    
    data = response.read()
    conn.close()


#=======================================================================
# DOOR SENSOR
#=======================================================================
def get_door_status():

    global GLOBAL_door_sensor_pin
            
    return pi.read(GLOBAL_door_sensor_pin)
    
    

#=======================================================================
# TOGGLE LED
#=======================================================================
def toggle_LED():

    global GLOBAL_next_call
    global GLOBAL_LED_display_time

    if GLOBAL_LED_display_time == True:
        print(datetime.datetime.now())

    #Prepare next thread time
    GLOBAL_next_call = GLOBAL_next_call + GLOBAL_LED_flash_rate
    threading.Timer( GLOBAL_next_call - time.time(), toggle_LED ).start()

    #Toggle LED
    if pi.read(GLOBAL_LED_pin) == 0:
        pi.write(GLOBAL_LED_pin, 1)
    else:
        pi.write(GLOBAL_LED_pin, 0)


#=======================================================================
# EXIT ROUTINE
#=======================================================================
def exit_code():

    global s

    #Set pins to OFF state
    pi.write(GLOBAL_LED_pin, 0)

    s.cancel()

    print('\nExiting program...')



#=======================================================================
# MAIN
#=======================================================================
def main():

    global GLOBAL_out_sensor_enable
    global GLOBAL_in_sensor_enable
    global GLOBAL_in_sensor_ref
    global GLOBAL_in_hum_sensor_enable
    global GLOBAL_thingspeak_enable_update
    global GLOBAL_update_rate
    global GLOBAL_LED_display_time
    global GLOBAL_door_sensor_enable
    global GLOBAL_screen_output


    #Check and action passed arguments
    if len(sys.argv) > 1:

        if '--outsensor=OFF' in sys.argv:
            GLOBAL_enable_out_temp_sensor = False

        if '--insensor=OFF' in sys.argv:
            GLOBAL_in_sensor_enable = False

        if '--thingspeak=OFF' in sys.argv:
            GLOBAL_thingspeak_enable_update = False

        if '--LEDtime=ON' in sys.argv:
            GLOBAL_LED_display_time = True
            
        if '--display=ON' in sys.argv:
            GLOBAL_screen_output = True

        if '--help' in sys.argv:
            print('usage: ./wstation.py {command}')
            print('')
            print('   --outsensor=OFF    - disables outside temperature monitoring')
            print('   --insensor=OFF     - disables inside temperature monitoring')
            print('   --thingspeak=OFF   - disable update to ThingSpeak')
            print('   --LEDtime=ON       - enables printing of LED toggle time')
            sys.exit(0)


    #Set up hardware
    setup_hardware()

    #Set up variables
    outside_temp    = 0
    inside          = {'temp':0 , 'hum':0}
    door_open       = 0

    sensor_data     = []
    sensors         = []

    if GLOBAL_out_sensor_enable == True:
        sensors.append('outside temp')

    if GLOBAL_in_sensor_enable == True:
        sensors.append('inside temp')
        sensors.append('inside hum')
        
    if GLOBAL_door_sensor_enable == True:
        sensors.append('door open')

    #Prepare thingspeak data to match sensor number
    for i in range(0, len(sensors)):
        sensor_data.append(0)

    if GLOBAL_thingspeak_enable_update == True and GLOBAL_screen_output == True:
        print('Thingspeak set up:')
        print(sensors)
        print(sensor_data)

    next_reading = time.time()

    #Main code
    try:
        while True:

            #Check door status
            if GLOBAL_door_sensor_enable == True:
                door_open = get_door_status()                
                sensor_data[GLOBAL_door_TS_field-1] = door_open
                
            #Get outside temperature
            if GLOBAL_out_sensor_enable == True:
                outside_temp = get_ds18b20_temp(GLOBAL_out_temp_sensor_ref)
                sensor_data[GLOBAL_out_temp_TS_field-1] = outside_temp

            #Get inside temperature and humidity
            if GLOBAL_in_sensor_enable == True:
                inside = get_dht22_data()
                sensor_data[GLOBAL_in_temp_TS_field-1] = inside['temp']
                sensor_data[GLOBAL_in_hum_TS_field-1] = inside['hum']

            #Display data on screen
            if GLOBAL_screen_output == True:
                output_data(sensors, sensor_data)

            #Send data to thingspeak
            if GLOBAL_thingspeak_enable_update == True:
                thingspeak_update_channel(GLOBAL_thingspeak_write_api_key, sensor_data)

            #Delay to give update rate
            next_reading += GLOBAL_update_rate
            sleep_length = next_reading - time.time()
            #print(sleep_length)
            if sleep_length > 0:
                time.sleep(sleep_length)

    except KeyboardInterrupt:
        exit_code()
        sys.exit(0)


#=======================================================================
# Boiler plate
#=======================================================================
if __name__=='__main__':
    main()
