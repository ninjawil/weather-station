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

#!/usr/bin/env python


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
UPDATE_RATE          = 300 # seconds
RRD_HEARTBEAT        = 2 # multiplier
W1_DEVICE_PATH       = '/sys/bus/w1/devices/'
DEBOUNCE_MICROS      = 0.250 #seconds

# --- RRDTool set up ---
RRDTOOL_RRD_DIR      = 'data'
RRDTOOL_RRD_FILE     = '/home/pi/weather/data/weather_data.rrd'
RRDTOOL_HEARTBEAT    = 2 # multiplier

# Consolidation type, Resolution (minutes), Recording Period (days)
RRDTOOL_RRA          = ('LAST',       5,  0.125, 
                        'AVERAGE',   15,      1,
                        'AVERAGE',   30,      2,
                        'AVERAGE',  120,      7,
                        'AVERAGE',  240,     31,
                        'AVERAGE',  720,     93,
                        'AVERAGE', 1440,    365,
                        'MIN',     1440,    365,
                        'MAX',     1440,    365)
 

# --- Set up thingspeak ----
THINGSPEAK_HOST_ADDR         = 'https://api.thingspeak.com'
THINGSPEAK_API_KEY_FILENAME  = 'thingspeak.txt'
THINGSPEAK_CHANNEL_ID        = '39722'


# --- Set up rain fall reed switch ----
PRECIP_TICK_MEASURE   = 0.3 #millimeters per tick
PRECIP_ACC_RESET_TIME = (00,00,00,00) #hour, minute, second, microsecond

ENABLE  = 0
PIN_REF = 1
UNIT    = 2
MIN     = 3
MAX     = 4
TYPE    = 5 

SENSOR_SET= {   'inside_temp':  (True, PIN_11, '*C', -50, 100, 'GAUGE'),
                'inside_hum':   (True, PIN_11, '%',  -1,  101, 'GAUGE'),
                'door_open':    (True, PIN_13, '',   -1,  2,   'GAUGE'),
                'precip_rate':  (True, PIN_15, 'mm', -5,  50,  'GAUGE'),
                'precip_acc':   (True, PIN_15, 'mm', -5,  500, 'GAUGE'),
                'outside_temp': (True, '28-0414705bceff',
                                               '*C', -50, 50,  'GAUGE')}
