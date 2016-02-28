#!usr/bin/env python

#===============================================================================
# IMPORT MODULES
#===============================================================================
# Standard Library
import ast
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
class error_msg:

    '''Sets up a error messaging system'''

    #---------------------------------------------------------------------------
    # PARENT CONSTRUCTOR
    #---------------------------------------------------------------------------
    def __init__(self, error_file_loc):

        self.error_file_location = error_file_loc
        self.logger = logging.getLogger('root')


    #---------------------------------------------------------------------------
    # SET ERROR
    #---------------------------------------------------------------------------
    def error_set(self, error_number):


    #---------------------------------------------------------------------------
    # CLEAR ERROR
    #---------------------------------------------------------------------------
    def error_clear(self, error_number):