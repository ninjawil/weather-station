#
# rrd_export.py
# Will De Freitas
#


#!/usr/bin/env python

'''Exports an XML file for each RRA set up from a RRD'''


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
def rrd_export(rrd_file, data_sources, rra_list, output_xml_folder):
    
    '''
    Exports and XML file per RRA from an RRD file.

        rrd_file -      rrd file location and script_name
        data_sources -  a list of the data_sources in the rrd file
        rra_list -      a dictionary of the RRA set up in the RRD. Should be in the 
                        format:
                            XML filename: (Consolidation type, Resolution (minutes), 
                                                                Recording Period (days))
                        e.g.
                            {'wd_avg_1d.xml':  ('LAST',       5,      1.17), 
                             'wd_avg_2d.xml':  ('AVERAGE',   30,      2)}
        output_xml_folder - folder to place output XML files.
    '''


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
        logger.error('System check failed ({error_v}). Exiting...'.format(
            error_v=e))
        sys.exit()


    #---------------------------------------------------------------------------
    # Check Rrd File And Set Up Sensor Variables
    #---------------------------------------------------------------------------
    try:
        rrd = rrd_tools.RrdFile(rrd_file)

        if sorted(rrd.ds_list()) != sorted(data_sources):
            logger.error('Data sources in RRD file does not match set up.')
            logger.error(rrd.ds_list())
            logger.error(data_sources)
            logger.error('Exiting...')
            sys.exit()
        else:
            logger.info('RRD fetch successful')

    except Exception, e:
        logger.error('RRD fetch failed ({error_v}). Exiting...'.format(error_v=e), 
                        exc_info=True)
        sys.exit()


    #---------------------------------------------------------------------------
    # Export RRD to XML
    #---------------------------------------------------------------------------
    for xml_file in rra_list:
        rrd.export( start= 'now-{rec_period:.0f}h'.format(rec_period= rra_list[xml_file][2] * 24),
                    end= 'now',
                    cf= rra_list[xml_file][0],
                    step= rra_list[xml_file][1] * 60,
                    ds_list= data_sources,
                    output_file= '{fd1}{fl}'.format(fd1= output_xml_folder, fl= xml_file))


    logger.info('--- Script Finished ---')


#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''


    rrd_export( rrd_file= '{fd1}{fd2}{fl}'.format(  fd1= s.SYS_FOLDER,
                                                    fd2= s.DATA_FOLDER,
                                                    fl= s.RRDTOOL_RRD_FILE),
                data_sources= list(s.SENSOR_SET.keys()),
                rra_list= s.RRDTOOL_RRA,
                output_xml_folder= '{fd1}{fd2}'.format( fd1= s.SYS_FOLDER, 
                                                        fd2= s.DATA_FOLDER))


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
