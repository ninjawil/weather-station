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
import time
import sys
import logging
import logging.handlers
import subprocess

# Third party modules
from crontab import CronTab

# Application modules
import settings as s
import rrd_tools


#===============================================================================
# Check script is running
#===============================================================================
def check_process_is_running(script_name):
    try:
        cmd1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(['grep', '-v', 'grep'], stdin=cmd1.stdout, 
                                stdout=subprocess.PIPE)
        cmd3 = subprocess.Popen(['grep', script_name], stdin=cmd2.stdout, 
                                stdout=subprocess.PIPE)
        return cmd3.communicate()[0] 

    except Exception, e:
        return e


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #--------------------------------------------------------------------------- 
    log_file = '/home/pi/weather/logs/wstation.log'

    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    logger.setLevel(logging.DEBUG)
        
    fh = logging.handlers.TimedRotatingFileHandler(filename=log_file, 
                                                    when='midnight', 
                                                    backupCount=7, 
                                                    utc=True)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info('--- Read Rain Gauge Script Started ---')


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    rrd = rrd_tools.RrdFile(s.RRDTOOL_RRD_FILE)

    if not os.path.exists(s.RRDTOOL_RRD_FILE):
        logger.debug(rrd.create_file(s.SENSOR_SET,
                                    s.RRDTOOL_RRA, 
                                    s.UPDATE_RATE, 
                                    s.RRDTOOL_HEARTBEAT,
                                    int(time.time() + s.UPDATE_RATE)))
        logger.info('RRD file not found. New file created')

    elif sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.error('Data sources in RRD file does not match set up.')
            sys.exit()

    else:
        logger.info('RRD file found and checked OK')


    #---------------------------------------------------------------------------
    # SCRIPTS
    #---------------------------------------------------------------------------

    #Set up to read sensors using cron job
    try:
        cmd='python /home/pi/weather/read_sensors.py'
        cron = CronTab()
        job = cron.new(command= cmd, comment= 'weather station job')
        if not cron.find_command(cmd):
            job.minute.every(s.UPDATE_RATE/60)
            cron.write()
            logger.info('CronTab file updated.')
            logger.debug(cron.render())
        else:
            logger.info('Command already in CronTab file')

    except ValueError:
        logger.error('CronTab file could not be updated. Exiting...')
        sys.exit()


    #Run read rain gauge script if not already running
    cmd = '/home/pi/weather/read_rain_gauge.py'
    script_not_running = check_process_is_running(cmd)
    if script_not_running:
        logger.info('Script read_rain_gauge.py already runnning.')
        logger.info(script_not_running)
    else:
        logger.info('Start Read Rain Gauge script')
        status = subprocess.Popen(['python', cmd])
        logger.info(status)


    logger.info('--- Wstation Script Finished ---')


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
