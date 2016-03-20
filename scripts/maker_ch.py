#!usr/bin/env python

#===============================================================================
# IMPORT MODULES
#===============================================================================
# Standard Library
import logging

# Third party modules
import requests
import requests.packages.urllib3

# Application modules


#!!! DISABLE WARNINGS ON PYTHON <2.7.9 !!!
requests.packages.urllib3.disable_warnings()


#===============================================================================
# CLASS DEFINITION AND FUNCTIONS
#===============================================================================
class MakerChannel:

    '''Sets up a Maker channel account'''

    #---------------------------------------------------------------------------
    # PARENT CONSTRUCTOR
    #--------------------------------------------------------------------------
    def __init__(self, addr, key, event_name):

        self.addr = addr
        self.key = key
        self.event = event_name
        self.logger = logging.getLogger('root')


    #---------------------------------------------------------------------------
    # GET REQUEST
    #---------------------------------------------------------------------------
    def trigger_an_event(self, **args):

        values = args
        cmd = '{host}{event}/with/key/{key}'.format(
                host=   self.addr,
                event=  self.event,
                key=    self.key)

        self.logger.debug('Trigger: {p}'.format(p= cmd))
        self.logger.debug('Values: {p}'.format(p= values))

        return requests.post(cmd, values)
