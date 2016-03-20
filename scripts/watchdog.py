#!usr/bin/env python

#===============================================================================
# Import modules
#===============================================================================
# Standard Library
import os
import sys
import time
import json
import logging

# Third party modules


# Application modules
import log
import maker_ch
import check_process


#===============================================================================
# CLASS DEFINITION AND FUNCTIONS
#===============================================================================
class AllErrors:

    def __init__(self, filename):
        self.logger     = logging.getLogger('root')
        self.file_loc   = filename


    #---------------------------------------------------------------------------
    # Open file
    #---------------------------------------------------------------------------
    def read_data(self):

        with open(self.file_loc, 'r') as f:
            return json.load(f)
        

    #---------------------------------------------------------------------------
    # Open file
    #---------------------------------------------------------------------------
    def write_data(self, data):

        with open(self.file_loc, 'w') as f:
            json.dump(data, f)
        

    #---------------------------------------------------------------------------
    # Clear error
    #---------------------------------------------------------------------------
    def clear(self):

        '''Removes timestamp from all error records'''

        errors = self.read_data()

        for error_code in errors:
            errors[error_code]['time'] = 0
            errors[error_code]['notified'] = 0
            errors[error_code]['count'] = 0

        self.write_data(errors)

        self.logger.info('Cleared all errors')



    #---------------------------------------------------------------------------
    # Check for errors in file
    #---------------------------------------------------------------------------
    def notify_via_maker_ch(self, maker_ch_addr, maker_ch_key):

        '''Load errors from json file and send unnotified errors. An active error
        is indicated by the presence of a timestamp.'''

        mc = maker_ch.MakerChannel(maker_ch_addr, maker_ch_key, 'WS_error')

        data_changed = False

        errors = self.read_data()

        for key in errors:
            if errors[key]['notified'] == 0 and errors[key]['time'] > 0:
                
                # Add a delay between event triggers
                if data_changed:
                    time.sleep(1)

                self.logger.info('Error notified: {err_msg}'.format(err_msg=errors[key]))
                
                # POST formatted time and error message to Maker channel
                mc.trigger_an_event(value1= time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(errors[key]['time'])), 
                                    value2= errors[key]['msg'])
                errors[key]['notified'] = 1
                data_changed = True
        
        if data_changed:
            self.write_data(errors)


#===============================================================================
class ErrorCode(AllErrors):

    '''
    Sets up a watchdog account. 
        filename    - Error JSON filename with complete path
    '''

    def __init__(self, filename, error_code):

        AllErrors.__init__(self, filename)
        self.err_code   = error_code


    #---------------------------------------------------------------------------
    # Check watchdog counter is being incremented then reset
    #---------------------------------------------------------------------------
    def increment_counter(self, step= 1):

        '''Increments the watchdog counter from an error code'''
    
        errors = self.read_data()
            
        errors[self.err_code]['watchdog'] += step

        self.write_data(errors)


    #---------------------------------------------------------------------------
    # Check watchdog counter is being incremented then reset
    #---------------------------------------------------------------------------
    def check_counter(self):

        '''Certain scripts will increment the counter when running. This 
        watchdog code will reset the tick back to zero. If this code finds that the 
        counter is not being incremented it will assume that the script has stopped
        running and throw an error.

        Returns a True if script is still running.'''

        errors = self.read_data()
            
        # check tick count is being incremented
        if errors[self.err_code]['watchdog'] > 0:
            script_ok = True
        else:
            script_ok = False

        # reset tick count
        errors[self.err_code]['watchdog'] = 0

        self.write_data(errors)

        return script_ok    


    #---------------------------------------------------------------------------
    # Set error
    #---------------------------------------------------------------------------
    def set(self):
        
        '''Add timestamp to error record if none present and clears notified 
        flag.'''

        errors = self.read_data()

        if errors[self.err_code]['time'] == 0:
            errors[self.err_code]['time'] = int(time.time())
            errors[self.err_code]['notified'] = 0
        
        errors[self.err_code]['count'] += 1

        self.write_data(errors)


    #---------------------------------------------------------------------------
    # Clear error
    #---------------------------------------------------------------------------
    def clear(self):

        '''Removes timestamp from error record'''

        errors = self.read_data()

        errors[self.err_code]['time'] = 0
        errors[self.err_code]['notified'] = 0
        errors[self.err_code]['count'] = 0

        self.write_data(errors)


#===============================================================================
# MAIN
#===============================================================================
def main():

    '''
    Entry point for the script.

    System arguments:
        --clear     - clears all errors
    '''
    
    script_name = os.path.basename(sys.argv[0])
    folder_loc  = os.path.dirname(os.path.realpath(sys.argv[0]))
    folder_loc  = folder_loc.replace('scripts', '')


    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= folder_loc,
                                                    script= script_name[:-3]))
    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name))  


    #---------------------------------------------------------------------------
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    if check_process.is_running(script_name):
        sys.exit()


    #---------------------------------------------------------------------------
    # CHECK FOR ERRORS AND NOTIFY
    #---------------------------------------------------------------------------    
    try:

        filename = '{fl}/data/error.json'.format(fl= folder_loc)

        #Check and action passed arguments
        if len(sys.argv) > 1:
            if '--clear' in sys.argv:
                wd = AllErrors(filename)
                wd.clear()

        else:
            wd_rain_counter = ErrorCode(filename, '0001')

            if not wd_rain_counter.check_counter():
                wd_rain_counter.set()

            with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
                config = json.load(f)

            wd_rain_counter.notify_via_maker_ch(config['maker_channel']['MAKER_CH_ADDR'],
                                                config['maker_channel']['MAKER_CH_KEY'])

    except Exception, e:
        logger.error('Update failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()

    finally:
        logger.info('--- Script Finished ---')


    
#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
