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
import time
import datetime
import logging

# Third party modules
import rrdtool

# Application modules
import settings as s
import rrd_tools as r


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
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''
 
    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------

    #Create RRD files if none exist
    if not os.path.exists('{directory}/{file_name}'.format(
                                        directory=s.RRDTOOL_RRD_DIR, 
                                        file_name=s.RRDTOOL_RRD_FILE)):

        logger.info('RRD file not found')
        logger.info(r.create_rrd_file(s.RRDTOOL_RRD_DIR, 
                                    s.RRDTOOL_RRD_FILE,
                                    s.SENSOR_SET,
                                    s.RRDTOOL_RRA, 
                                    s.UPDATE_RATE, 
                                    s.RRDTOOL_HEARTBEAT,
                                    datetime.datetime.now() + s.UPDATE_RATE))
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
