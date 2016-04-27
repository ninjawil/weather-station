#!/usr/bin/env python

'''Checks processes'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import subprocess
import logging

# Third party modules


# Application modules



#===============================================================================
# Check script is running
#===============================================================================
def is_running(script_name):

    '''Checks list of processes for script name and filters out lines with the 
    PID and parent PID. Returns a TRUE if other script with the same name is
    found running.'''

    try:
        logger = logging.getLogger('root')

        cmd1 = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(['grep', '-v', 'grep'], stdin=cmd1.stdout, 
                                stdout=subprocess.PIPE)
        cmd3 = subprocess.Popen(['grep', '-v', str(os.getpid())], stdin=cmd2.stdout, 
                                stdout=subprocess.PIPE)
        cmd4 = subprocess.Popen(['grep', '-v', str(os.getppid())], stdin=cmd3.stdout, 
                                stdout=subprocess.PIPE)
        cmd5 = subprocess.Popen(['grep', script_name], stdin=cmd4.stdout, 
                                stdout=subprocess.PIPE)

        other_script_found = cmd5.communicate()[0]

        if other_script_found:
            logger.info('Script already runnning. Exiting...')
            logger.info(other_script_found)
            return True

        return False

    except Exception, e:
        logger.error('System check failed ({error_v}). Exiting...'.format(
            error_v=e))
        return True
