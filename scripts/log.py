#!/usr/bin/env python

'''Provides a common logging set up for all scripts'''


#===============================================================================
# Import modules
#===============================================================================
import logging
import logging.handlers
import time


#===============================================================================
# Custom logger
#===============================================================================
def setup(name, log_file):
   
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)-8s] %(module)-15s : %(message)s')
    logging.Formatter.converter = time.gmtime
    
    fh = logging.handlers.TimedRotatingFileHandler(filename=log_file, 
                                                    when='midnight', 
                                                    backupCount=7, 
                                                    utc=True)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
