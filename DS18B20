#-----------------------------------------------------------------------
#
# Reads data from a DS18B20 temperature sensor
#
#-----------------------------------------------------------------------

#!usr/bin/env python

#=======================================================================
# Import modules
#=======================================================================
import os, sys


#=======================================================================
# LOAD DRIVERS
#=======================================================================
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


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
