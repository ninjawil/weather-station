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
else:
    GLOBAL_Pin_11   = 11
    GLOBAL_Pin_12   = 12


# --- System set up ---
GLOBAL_update_rate          = 0.025 * 60  # seconds
GLOBAL_w1_device_path       = '/sys/bus/w1/devices/'


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


# --- Set up flashing LED ----
GLOBAL_LED_display_time     = False
GLOBAL_LED_pin              = GLOBAL_Pin_12
GLOBAL_LED_flash_rate       = 1  # seconds
GLOBAL_next_call            = time.time()



#=======================================================================
# SETUP DEVICE
#=======================================================================
def setup():
    
    #Set up DHT22
    global s
    global GLOBAL_in_sensor_pin
    
    s = DHT22.sensor(pi, GLOBAL_in_sensor_pin)
    
    
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
        
    return {'temp':s.temperature(), 'hum':s.humidity()}


#=======================================================================
# OUTPUT
#=======================================================================
def output_data(sensors, data):
    
    #Check passed data is correct
    if len(sensors) <= len(data):
        
        #Print date and time
        print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
        
        field = 0
        
        # Display each sensor data
        for i in sensors:
            
            #Check for unit
            if 'temp' in i:
                unit = u'\u00b0C'
            else:
                unit = '%'
            
            #Print sensor data
            print(i+'\t'+str(data[field])+unit)
            
            #Next data field
            field += 1
    
 
    
#=======================================================================
# UPDATE THINGSPEAK CHANNEL
#=======================================================================
def thingspeak_update_channel(channel, field_data):
    
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
    print('Data sent to thingspeak: ' + response.reason + '\t status: ' + str(response.status)+'\n')
    data = response.read()
    conn.close()
 
 
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
        
    #Set pins to OFF state
    pi.write(GLOBAL_LED_pin, 0)
    
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
            
        if '--help' in sys.argv:
            print('usage: ./wstation.py {command}')
            print('\n')
            print('--outsensor=OFF    - disables outside temperature monitoring')
            print('--thingspeak=OFF - disable update to ThingSpeak')
            print('--LEDtime=ON     - enables printing of LED toggle time')
    
    
    #Set up variables   
    setup()
    
    outside_temp    = 0
    inside          = {'temp':0 , 'hum':0}
    
    thingspeak_data = [0,0,0,0,0,0,0,0]
    
    sensors         = []
    
    if GLOBAL_out_sensor_enable == True:
        sensors.append('outside temp')

    if GLOBAL_in_sensor_enable == True:
        sensors.append('inside temp')
        sensors.append('inside hum')

    
    #Main code
    try:
        while True:
            
            #Get outside temperature
            if GLOBAL_out_sensor_enable == True:
                outside_temp = get_ds18b20_temp(GLOBAL_out_temp_sensor_ref)
                thingspeak_data[GLOBAL_out_temp_TS_field-1] = outside_temp
            
            #Get inside temperature and humidity
            if GLOBAL_in_sensor_enable == True:
                inside = get_dht22_data()
                thingspeak_data[GLOBAL_in_temp_TS_field-1] = inside['temp']
                thingspeak_data[GLOBAL_in_hum_TS_field-1] = inside['hum']
                
            #Display data on screen
            output_data(sensors, thingspeak_data)
                
            #Send data to thingspeak
            if GLOBAL_thingspeak_enable_update == True:
                thingspeak_update_channel(GLOBAL_thingspeak_write_api_key, thingspeak_data)
                            
            #Delay to give update rate
            time.sleep(GLOBAL_update_rate)
    
    except KeyboardInterrupt:
        exit_code()
        sys.exit(0)


#=======================================================================
# Boiler plate
#=======================================================================
if __name__=='__main__':
    main()



