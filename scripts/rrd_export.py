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

'''Exports current RRD to XML'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import time
import sys
import subprocess
import collections

# Third party modules

# Application modules
import log
import settings as s
import rrd_tools
import check_process


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''


    script_name = os.path.basename(sys.argv[0])


    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= s.SYS_FOLDER,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name))


    #---------------------------------------------------------------------------
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    try:
        other_script_found = check_process.is_running(script_name)

        if other_script_found:
            logger.critical('Script already runnning. Exiting...')
            logger.error(other_script_found)
            sys.exit()

    except Exception, e:
        logger.critical('System check failed ({error_v}). Exiting...'.format(
            error_v=e))
        sys.exit()


    #---------------------------------------------------------------------------
    # Check Rrd File And Set Up Sensor Variables
    #---------------------------------------------------------------------------
    try:
        rrd = rrd_tools.RrdFile('{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                                        fd2= s.DATA_FOLDER,
                                                        fl= sRRDTOOL_RRD_FILE)

        if sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.critical('Data sources in RRD file does not match set up.')
            logger.error(rrd.ds_list())
            logger.error(list(s.SENSOR_SET.keys()))
            logger.error('Exiting...')
            sys.exit()
        else:
            logger.info('RRD fetch successful')

    except Exception, e:
        logger.critical('RRD fetch failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()


    #---------------------------------------------------------------------------
    # Export RRD to XML
    #---------------------------------------------------------------------------
    rd = collections.namedtuple('ss', 'cf res period')
    rra_set = {k: rd(*s.RRDTOOL_RRA[k]) for k in s.RRDTOOL_RRA}

    for key in sorted(rra_set.keys()):
        rrd.export( start= '-{days}d'.format(rra_set[key].period), 
                    end= 'now', 
                    step= rra_set[key].res * 60, 
                    ds_list= list(s.SENSOR_SET.keys()), 
                    output_file= '{fd1}{fd2}{fl}'.format(fd1= s.SYS_FOLDER,
                                                         fd2= s.DATA_FOLDER, 
                                                         fl= key), 
                    cf= rra_set[key].cf)





    logger.info('--- Script Finished ---')


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
