#!/usr/bin/env python

'''Checks processes'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import subprocess

# Third party modules


# Application modules



#===============================================================================
# Check script is running
#===============================================================================
def is_running(script_name):

    '''Checks list of processes for script name and filters out lines with the 
    PID and parent PID. Returns None if no other scripts with the same name are
    running otherwise returns the line of the ps -ef with those PIDs. Error
    value is returned instead.'''

    try:
        cmd1 = subprocess.Popen(['ps', '-ef'], stdout=subprocess.PIPE)
        cmd2 = subprocess.Popen(['grep', '-v', 'grep'], stdin=cmd1.stdout, 
                                stdout=subprocess.PIPE)
        cmd3 = subprocess.Popen(['grep', '-v', str(os.getpid())], stdin=cmd2.stdout, 
                                stdout=subprocess.PIPE)
        cmd4 = subprocess.Popen(['grep', '-v', str(os.getppid())], stdin=cmd3.stdout, 
                                stdout=subprocess.PIPE)
        cmd5 = subprocess.Popen(['grep', script_name], stdin=cmd4.stdout, 
                                stdout=subprocess.PIPE)
        return cmd5.communicate()[0] 

    except Exception, e:
        return e