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
import watchdog as wd


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
    folder_loc  = os.path.dirname(os.path.realpath(sys.argv[0]))
    folder_loc  = folder_loc.replace('scripts', '')


    #---------------------------------------------------------------------------
    # Set up logger
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= folder_loc,
                                                    script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name)) 
    

    #---------------------------------------------------------------------------
    # SET UP WATCHDOG
    #---------------------------------------------------------------------------
    err_file    = '{fl}/data/error.json'.format(fl= folder_loc)
    wd_err      = wd.ErrorCode(err_file, '0006')


    #---------------------------------------------------------------------------
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    if check_process.is_running(script_name):
        wd_err.set()
        sys.exit()
  

    #---------------------------------------------------------------------------
    # Check Rrd File
    #---------------------------------------------------------------------------
    rrd = rrd_tools.RrdFile('{fd1}/data/{fl}'.format(fd1= folder_loc,
                                                    fl= s.RRDTOOL_RRD_FILE))
        
    if not rrd.check_ds_list_match(list(s.SENSOR_SET.keys())):
        wd_err.set()
        sys.exit()


    #---------------------------------------------------------------------------
    # Export RRD to XML
    #---------------------------------------------------------------------------
    try:
        for xml_file in rra_list:
            rrd.export( start= 'now-{rec_period:.0f}h'.format(
                                        rec_period= rra_list[xml_file][2] * 24),
                        end= 'now',
                        cf= rra_list[xml_file][0],
                        step= rra_list[xml_file][1] * 60,
                        ds_list= data_sources,
                        output_file= '{fd1}{fl}'.format(fd1= output_xml_folder, 
                                                        fl= xml_file))
    except ValueError:
        logger.warning('Failed to export RRD ({value_error})'.format(
            value_error=ValueError))
        wd_err.set()
                

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

    time.sleep(3)

    rrd_tools.avg_max_min_to_xml('{fd1}/data/{fd2}'.format(fd1= s.SYS_FOLDER, 
                                                            fd2= 'wd_max_1y.xml'), 
                                 '{fd1}/data/{fd2}'.format(fd1= s.SYS_FOLDER, 
                                                            fd2= 'wd_min_1y.xml'),
                                 '{fd1}/data/{fd2}'.format(fd1= s.SYS_FOLDER, 
                                                            fd2= 'wd_avg_1y.xml'), 
                                 '{fd1}/data/{fd2}'.format(fd1= s.SYS_FOLDER, 
                                                            fd2= 'wd_all_1y.xml'))


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
