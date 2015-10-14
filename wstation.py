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
import log

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
    logger = log.setup('root', '/home/pi/weather/logs/wstation.log')

    logger.info('--- Read Rain Gauge Script Started ---')


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    rrd = rrd_tools.rrd_file(s.RRDTOOL_RRD_FILE)

    if not os.path.exists(s.RRDTOOL_RRD_FILE):
        logger.debug(rrd.create_file(s.SENSOR_SET,
                                    s.RRDTOOL_RRA, 
                                    s.UPDATE_RATE, 
                                    s.RRDTOOL_HEARTBEAT,
                                    int(time.time() + s.UPDATE_RATE)))
        logger.info('RRD file not found. New file created')

    else:
        logger.info('RRD file found')

        if sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.critical('Data sources in RRD file does not match set up')
            sys.exit()



    #---------------------------------------------------------------------------
    # RUN SCRIPTS
    #---------------------------------------------------------------------------

    #Set up to read sensors using cron job
    try:
        cmd='python /home/pi/weather/read_sensors.py'
        cron = CronTab()
        job = cron.new(command= cmd, comment= 'weather station job')
        #if not cron.find_command(cmd):
            #job.minute.during(0,55).every(s.UPDATE_RATE/60)
        job.minute.on(0, 5, 10, 15, 20 ,25, 30, 35 ,40, 45, 50, 55)
        cron.write()
        logger.info('CronTab file updated.')
        logger.debug(cron.render())

    except ValueError:
        logger.critical('CronTab file could not be updated. Exiting...')
        sys.exit()


    logger.info('Start Read Rain Gauge script')
    #read_rain_gauge.main()

#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
