#-------------------------------------------------------------------------------
#
# 'Controls shed weather station
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

'''Gathers data from various sensors to capture weather conditiona and take
apropriate actions in shed.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import threading
import time
import datetime
import logging

# Third party modules
import rrdtool

# Application modules
import settings as s


#===============================================================================
# Set up logger
#===============================================================================
log_directory = 'logs'
log_file = 'wstation.log'

if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(filename='{directory}/{file_name}'.format(
                                directory=log_directory, 
                                file_name=log_file), 
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)
logger.info('--- Read Rain Gauge Script Started ---')
script_start_time = datetime.datetime.now()
logger.info('Script start time: {start_time}'.format(
    start_time=script_start_time.strftime('%Y-%m-%d %H:%M:%S'))) 




#===============================================================================
# TOGGLE LED
#===============================================================================
def create_rrd_data_source(source_name, source_type, source_heartbeat, 
                            source_min, source_max):
    return 'DS:{ds_name}:{ds_type}:{ds_hb}:{ds_min}:{ds_max}'.format(
        ds_name=source_name.replace(' ','_'),
        ds_type=source_type,
        ds_hb=source_heartbeat,
        ds_min=source_min,
        ds_max=source_max)

    

#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''


    #Set initial variable values
    rain_sensor_enable           = True
    out_sensor_enable            = True
    in_sensor_enable             = True
    thingspeak_enable_update     = True
    door_sensor_enable           = True
    
    rrd_data_sources             = []
    rrd_set                      = []

    
    #---------------------------------------------------------------------------
    # SET UP OUTSIDE TEMPERATURE SENSOR
    #---------------------------------------------------------------------------
    if out_sensor_enable:
        rrd_data_sources += [create_rrd_data_source(s.OUT_TEMP_NAME, 
                                                    s.OUT_TEMP_TYPE,
                                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                                    str(s.OUT_TEMP_MIN),
                                                    str(s.OUT_TEMP_MAX))]


    #---------------------------------------------------------------------------
    # SET UP INSIDE TEMPERATURE SENSOR
    #---------------------------------------------------------------------------
    if in_sensor_enable:
        rrd_data_sources += [create_rrd_data_source(s.IN_TEMP_NAME, 
                                                    s.IN_TEMP_TYPE,
                                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                                    str(s.IN_TEMP_MIN),
                                                    str(s.IN_TEMP_MAX))]
        rrd_data_sources += [create_rrd_data_source(s.IN_HUM_NAME, 
                                                    s.IN_HUM_TYPE,
                                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                                    str(s.IN_HUM_MIN),
                                                    str(s.IN_HUM_MAX))]

    
    #---------------------------------------------------------------------------
    # SET UP DOOR SENSOR
    #---------------------------------------------------------------------------
    if door_sensor_enable:
        rrd_data_sources += [create_rrd_data_source(s.DOOR_NAME, 
                                                    s.DOOR_TYPE,
                                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                                    str(s.DOOR_MIN),
                                                    str(s.DOOR_MAX))]


    #---------------------------------------------------------------------------
    # SET UP RAIN SENSOR
    #---------------------------------------------------------------------------
    if rain_sensor_enable:
        rrd_data_sources += [create_rrd_data_source(s.PRECIP_RATE_NAME, 
                                                    s.PRECIP_RATE_TYPE,
                                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                                    str(s.PRECIP_RATE_MIN),
                                                    str(s.PRECIP_RATE_MAX))]
        rrd_data_sources += [create_rrd_data_source(s.PRECIP_ACCU_NAME, 
                                                    s.PRECIP_ACCU_TYPE,
                                                    str(s.RRDTOOL_HEARTBEAT*s.UPDATE_RATE),
                                                    str(s.PRECIP_ACCU_MIN),
                                                    str(s.PRECIP_ACCU_MAX))]                               


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    if rrdtool_enable_update:
        #Set up inital values for variables
        rra_files        = []
  
        #Prepare RRA files
        for i in range(0,len(s.RRDTOOL_RRA),3):
            rra_files.append('RRA:{cf}:0.5:{steps}:{rows}'.format(
                cf=s.RRDTOOL_RRA[i],
                steps=str((s.RRDTOOL_RRA[i+1]*60)/s.UPDATE_RATE),
                rows=str(((s.RRDTOOL_RRA[i+2])*24*60)/s.RRDTOOL_RRA[i+1])))
 
        #Prepare RRD set
        rrd_set = [s.RRDTOOL_RRD_FILE, 
                    '--step', '{step}'.format(step=s.UPDATE_RATE), 
                    '--start', '{start_time:.0f}'.format(start_time=next_reading)]
        rrd_set +=  rrd_data_sources + rra_files
        
        #Create RRD files if none exist
        if not os.path.exists(s.RRDTOOL_RRD_FILE):
            logger.info('RRD file not found')
            logger.info(rrd_set)
            rrdtool.create(rrd_set)
            logger.info('New RRD file created')
        else:
            #Fetch data from round robin database & extract next entry time to sync loop
            logger.info('RRD file found')
            data_values = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                        '-s', str(s.UPDATE_RATE * -2))
            next_reading  = data_values[0][1]
            logger.info('RRD FETCH: Next sensor reading at {time}'.format(
                time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(next_reading))))


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
