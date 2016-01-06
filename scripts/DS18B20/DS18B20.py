#!/usr/bin/env python

#===============================================================================
# IMPORT MODULES
#===============================================================================
import os
import time


#===============================================================================
# LOAD DRIVERS
#===============================================================================
os.system('modprobe w1-gpio gpiopin=19')
os.system('modprobe w1-therm')


#===============================================================================
class DS18B20:
 
    '''Sets up a DS18B20 sensor'''
 
    def __init__(self, device_id, device_path):
        self.id = device_id
        self.path = device_path
 
 
    #---------------------------------------------------------------------------
    # READ RAW DATA FROM W1 SLAVE
    #---------------------------------------------------------------------------
    def w1_slave_read(self):
        '''Read w1 slave'''
        with open(self.path + self.id + '/w1_slave', 'r') as f:
            return f.readlines()


    #---------------------------------------------------------------------------
    # READ DATA FROM DS18B20
    #---------------------------------------------------------------------------
    def get_temp(self):

        lines = self.w1_slave_read()

        #If unsuccessful first read loop until temperature acquired
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.w1_slave_read()

        temp_output = lines[1].find('t=')

        if temp_output != -1:
            return float(lines[1].strip()[temp_output+2:]) / 1000.0
        else:
            return None

