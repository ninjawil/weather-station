#-------------------------------------------------------------------------------
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

#===============================================================================
# IMPORT MODULES
#===============================================================================
import os
import time


#===============================================================================
# LOAD DRIVERS
#===============================================================================
os.system('modprobe w1-gpio')
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

