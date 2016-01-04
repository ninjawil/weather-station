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
    Initates scripts via cronjobs.'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys


# Third party modules

# Application modules
import log
import settings as s
import rrd_tools


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    script_name = os.path.basename(sys.argv[0])

    #---------------------------------------------------------------------------
    # Set up logger
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= s.SYS_FOLDER,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name)) 


    #---------------------------------------------------------------------------
    # SET UP RRD DATA AND TOOL
    #---------------------------------------------------------------------------
    rrd = rrd_tools.RrdFile(s.RRDTOOL_RRD_FILE)

    if not os.path.exists(s.RRDTOOL_RRD_FILE):
        rrd.create_file(s.SENSOR_SET, 
                        s.RRDTOOL_RRA, 
                        s.UPDATE_RATE, 
                        s.RRDTOOL_HEARTBEAT, 
                        int(time.time() + s.UPDATE_RATE))
        logger.info('RRD file not found. New file created')

    elif sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.error('Data sources in RRD file does not match set up.')
            sys.exit()

    else:
        logger.info('RRD file found and checked OK')



    #---------------------------------------------------------------------------
    # SCRIPTS
    #---------------------------------------------------------------------------

    #Set up CRONTAB


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
