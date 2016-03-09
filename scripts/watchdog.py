#!usr/bin/env python

#===============================================================================
# Import modules
#===============================================================================
# Standard Library
import os
import sys
import datetime
import time
import collections
import json
import logging

# Third party modules


# Application modules
import settings as s
import log
import check_process
import maker_ch



#===============================================================================
# Send to Maker channel
#===============================================================================
def send_to_maker_ch(event, v1= '', v2= '', v3= ''):

    '''Load Maker Channel details from config.json file, set up an instance
    for the event and send data.'''

    logger = logging.getLogger('root')

    try:
        with open('{fl}/data/config.json'.format(fl= s.SYS_FOLDER), 'r') as f:
            config = json.load(f)

        maker_ch_addr  = config['maker_channel']['MAKER_CH_ADDR']
        maker_ch_key   = config['maker_channel']['MAKER_CH_KEY']

        mc = maker_ch.MakerChannel(maker_ch_addr, maker_ch_key, event)

        mc.trigger_an_event(value1= v1,
                            value2= v2,
                            value3= v3)
        
    except Exception, e:
        logger.error('Failed to send data ({error_v}). Exiting...'.format(
        error_v=e))
        sys.exit()


#===============================================================================
# Check for errors in file
#===============================================================================
def notify_errors():

    '''Load errors from json file and send unnotified errors'''

    logger = logging.getLogger('root')

    with open('{fl}/data/error.json'.format(fl= s.SYS_FOLDER), 'r') as f:
        errors = json.load(f)

    for key in errors:
        if errors[key]['notified'] == 0 and errors[key]['time'] > 0:
            logger.info('Error notified: {err_msg}'.format(err_msg=errors[key]))
            send_to_maker_ch('WS_error', 
                              v1= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(errors[key]['time'])), 
                              v2= errors[key]['msg'])
            errors[key]['notified'] = 1
            data_changed = True
    
    if data_changed:
        with open('{fl}/data/error.json'.format(fl= s.SYS_FOLDER), 'w') as f:
            f.write(json.dumps(errors))


#===============================================================================
# MAIN
#===============================================================================
def main():

    '''
    
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
    # CHECK FOR ERRORS AMD SEND 
    #---------------------------------------------------------------------------    
    try:

        notify_errors()


    
        logger.info('--- Script Finished ---')


    except Exception, e:
        logger.error('Update failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()

    
#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
