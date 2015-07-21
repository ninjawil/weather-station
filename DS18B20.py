#-----------------------------------------------------------------------
#
# Reads data from a DS18B20 temperature sensor
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
#-----------------------------------------------------------------------

#!usr/bin/env python

#=======================================================================
# Import modules
#=======================================================================
import os
import sys


#=======================================================================
# LOAD DRIVERS
#=======================================================================
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


#=======================================================================
# READ RAW DATA FROM W1 SLAVE
#=======================================================================
def w1_slave_read(w1_device_path, device_id):

    device_id = w1_device_path+device_id+'/w1_slave'

    f=open(device_id,'r')
    lines=f.readlines()
    f.close()

    return lines


#=======================================================================
# READ DATA FROM DS18B20
#=======================================================================
def get_temp(w1_device_path, device_id):

    lines = w1_slave_read(w1_device_path, device_id)

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
