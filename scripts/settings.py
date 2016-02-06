#!/usr/bin/env python


#===============================================================================
# GLOBAL CONSTANTS
#===============================================================================

# --- Set up GPIO referencing----
broadcom_ref     = True

if broadcom_ref:
    PIN_11 = 17
    PIN_12 = 18
    PIN_13 = 27
    PIN_15 = 22
    PIN_37 = 26
    PIN_38 = 20
    PIN_40 = 21
else: 
    PIN_11 = 11
    PIN_12 = 12
    PIN_13 = 13
    PIN_15 = 15
    PIN_37 = 37
    PIN_38 = 38
    PIN_40 = 40


# --- System set up ---
UPDATE_RATE         = 300 # seconds
W1_DEVICE_PATH      = '/sys/bus/w1/devices/'
DEBOUNCE_MICROS     = 0.250 #seconds
SYS_FOLDER          = '/home/pi/weather'
DATA_FOLDER         = '/data/'
TICK_DATA           = 'tick_count'

# --- RRDTool set up ---
RRDTOOL_RRD_FILE     = 'weather_data.rrd'
RRDTOOL_HEARTBEAT    = 2 # multiplier

# XML filename: Consolidation type, Resolution (minutes), Recording Period (days) 
RRDTOOL_RRA =  {'wd_last_1d.xml': ('LAST',       5,      1.17), 
                'wd_avg_2d.xml':  ('AVERAGE',   30,      2), 
                'wd_avg_1w.xml':  ('AVERAGE',  120,      7), 
                'wd_avg_1m.xml':  ('AVERAGE',  240,     31), 
                'wd_avg_3m.xml':  ('AVERAGE',  720,     93), 
                'wd_avg_1y.xml':  ('AVERAGE', 1440,    365), 
                'wd_min_1y.xml':  ('MIN',     1440,    365), 
                'wd_max_1y.xml':  ('MAX',     1440,    365)}
 

SENSOR_SET= {   'inside_temp':  (True, PIN_37, '*C', -50, 100, 'GAUGE'),
                'inside_hum':   (True, PIN_37, '%',  -1,  101, 'GAUGE'),
                'door_open':    (True, PIN_40, '',   -1,  2,   'GAUGE'),
                'precip_rate':  (True, PIN_38, 'mm', -5,  50,  'GAUGE'),
                'precip_acc':   (True, PIN_38, 'mm', -5,  500, 'GAUGE'),
                'outside_temp': (True, '28-0414705bceff',
                                               '*C', -50, 50,  'GAUGE'),
                'sw_status':    (True, '',     '',   -1,  2,   'GAUGE'),
                'sw_power':     (True, '', 'W',  -9999,  9999, 'GAUGE')}
