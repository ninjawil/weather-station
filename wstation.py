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

'''Sets up the enviroment to run the weather station.

    Begins by checking that an RRD file exists and that the data sources are 
    correct. If no RRD file found then create a new one.

    Initates scripts via cronjobs.

    Rain gauge has a looping script - initiated by this script.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import logging

# Third party modules
from crontab import CronTab


# Application modules
import settings as s
import rrd_tools


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #--------------------------------------------------------------------------- 
    log_file = 'logs/wstation.log'

    logging.basicConfig(filename='{file_name}'.format(file_name=log_file), 
                        level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.info('--- Read Rain Gauge Script Started ---')


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    rrd = rrd_tools.rrd_file(s.RRDTOOL_RRD_FILE)

    if not os.path.exists(s.RRDTOOL_RRD_FILE):
        logger.info(rrd.create_file(s.SENSOR_SET,
                                    s.RRDTOOL_RRA, 
                                    s.UPDATE_RATE, 
                                    s.RRDTOOL_HEARTBEAT,
                                    int(time.time() + s.UPDATE_RATE)))
        logger.info('RRD file not found. New file created')

    else:
        logger.info('RRD file found')
        if sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.error('Data sources in RRD file does not match set up')



    #---------------------------------------------------------------------------
    # RUN SCRIPT
    #---------------------------------------------------------------------------
    #read_rain_gauge.main()

    #Set up to read sensors using cron job
    cron = CronTab()
    job = cron.new(command='read_sensors.py')
    if not cron.find_command('read_sensors.py'):
        #job.minute.during(0,55).every(s.UPDATE_RATE/60)
        job.minute.on(0, 5, 10, 15, 20 ,25, 30, 35 ,40, 45, 50, 55)
        #job.minute.on([i for i in range(0, 60, s.UPDATE_RATE/60)])


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
