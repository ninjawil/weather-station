#-------------------------------------------------------------------------------
#
# Shed weather station set up file
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
# GLOBAL CONSTANTS
#===============================================================================

# --- Set up GPIO referencing----
broadcom_ref     = True

if broadcom_ref:
    PIN_11   = 17
    PIN_12   = 18
    PIN_13   = 27
    PIN_15   = 22
else:
    PIN_11   = 11
    PIN_12   = 12
    PIN_13   = 13
    PIN_15   = 15


# --- System set up ---
UPDATE_RATE          = 5 # seconds
W1_DEVICE_PATH       = '/sys/bus/w1/devices/'
DEBOUNCE_MICROS      = 0.250 #seconds


# --- Set up thingspeak ----
THINGSPEAK_HOST_ADDR         = 'api.thingspeak.com:80'
THINGSPEAK_API_KEY_FILENAME  = 'thingspeak.txt'


# --- Set up outside DS18B20 sensor ----
OUT_TEMP_SENSOR_REF  = '28-0414705bceff'
OUT_TEMP_TS_FIELD    = 1


# --- Set up inside DHT22 sensor ----
IN_SENSOR_REF        = 'DHT22'
IN_SENSOR_PIN        = PIN_11
IN_TEMP_TS_FIELD     = 2
IN_HUM_TS_FIELD      = 3


# --- Set up door reed switch ----
DOOR_SENSOR_PIN      = PIN_13
DOOR_TS_FIELD        = 4


# --- Set up rain fall reed switch ----
PRECIP_SENSOR_PIN     = PIN_15
PRECIP_RATE_TS_FIELD  = 5
PRECIP_ACCU_TS_FIELD  = 6
PRECIP_TICK_MEASURE   = 0.6 #millimeters per tick
PRECIP_ACC_RESET_TIME = [23,59,0,0] #hour, minute, second, microsecond


# --- Set up flashing LED ----
LED_PIN              = PIN_12
LED_FLASH_RATE       = 1  # seconds
