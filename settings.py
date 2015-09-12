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
LOG_FILENAME         = 'wstation.log'


#Sensor list set up
TS_FIELD             = 0
UNIT                 = 1
VALUE                = 2


# --- RRDTool set up ---
RRDTOOL_RRD_FILE     = 'weather_data.rrd'
RRDTOOL_HEARTBEAT    = 2 # multiplier
RRDTOOL_RRA          = ('LAST',       5,  0.125,  # Consolidation type, Resolution (minutes), Recording Period (days)
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


# --- Set up outside DS18B20 sensor ----
OUT_TEMP_NAME        = 'outside temp'
OUT_TEMP_UNIT        = '*C' #u'\u00b0C'
OUT_TEMP_SENSOR_REF  = '28-0414705bceff'
OUT_TEMP_TS_FIELD    = 1
OUT_TEMP_MIN         = -50
OUT_TEMP_MAX         = 50
OUT_TEMP_TYPE        = 'GAUGE'

# --- Set up inside DHT22 sensor ----
IN_SENSOR_REF        = 'DHT22'
IN_SENSOR_PIN        = PIN_11
IN_TEMP_NAME         = 'inside temp'
IN_TEMP_UNIT         = '*C' #u'\u00b0C'
IN_TEMP_TS_FIELD     = 2
IN_TEMP_MIN          = -50
IN_TEMP_MAX          = 100
IN_TEMP_TYPE         = 'GAUGE'

IN_HUM_NAME          = 'inside hum'
IN_HUM_UNIT          = '%'
IN_HUM_TS_FIELD      = 3
IN_HUM_MIN           = -1
IN_HUM_MAX           = 101
IN_HUM_TYPE          = 'GAUGE'


# --- Set up door reed switch ----
DOOR_NAME            = 'door open'
DOOR_UNIT            = ''
DOOR_SENSOR_PIN      = PIN_13
DOOR_TS_FIELD        = 4
DOOR_MIN             = -1
DOOR_MAX             = 2
DOOR_TYPE            = 'GAUGE'


# --- Set up rain fall reed switch ----
PRECIP_SENSOR_PIN     = PIN_15
PRECIP_TICK_MEASURE   = 0.3 #millimeters per tick
PRECIP_ACC_RESET_TIME = (00,00,00,00) #hour, minute, second, microsecond

PRECIP_RATE_NAME      = 'precip rate'
PRECIP_RATE_UNIT      = 'mm'
PRECIP_RATE_TS_FIELD  = 5
PRECIP_RATE_MIN       = -5
PRECIP_RATE_MAX       = 50
PRECIP_RATE_TYPE      = 'GAUGE'

PRECIP_ACCU_NAME      = 'precip acc'
PRECIP_ACCU_UNIT      = 'mm'
PRECIP_ACCU_TS_FIELD  = 6
PRECIP_ACCU_MIN       = -5
PRECIP_ACCU_MAX       = 500
PRECIP_ACCU_TYPE      = 'GAUGE'


# --- Set up flashing LED ----
LED_PIN              = PIN_12
LED_FLASH_RATE       = 1  # seconds
