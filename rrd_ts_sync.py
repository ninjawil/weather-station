#-------------------------------------------------------------------------------
#
# Controls shed weather station
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

#!usr/bin/env python

#===============================================================================
# Import modules
#===============================================================================
# Standard Library
import sys
import datetime
import collections

# Third party modules

# Application modules
import thingspeak
import rrd_tools
import settings as s
import log


#===============================================================================
# MAIN
#===============================================================================
def main():

    '''Synchronizes thingspeak account with the data in the local Round Robin
        database.

        Starts by grabing some data from thingspeak to check all sensors are 
        present.

        Then checks all sensors are also present in the RRD database.

        If any of these checks fail, the script ends with an error.


    '''
   

    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = log.setup('root', '/home/pi/weather/logs/rrd_ts_sync.log')

    logger.info('--- RRD To Thingspeak Sync Script Started ---')   
    

    #---------------------------------------------------------------------------
    # SET UP THINGSPEAK ACCOUNT
    #---------------------------------------------------------------------------
    try:
        ts_acc = thingspeak.TSChannel(s.THINGSPEAK_HOST_ADDR,
                                      file= s.THINGSPEAK_API_KEY_FILENAME,
                                      ch_id= s.THINGSPEAK_CHANNEL_ID)
        
        ch_feed = ts_acc.get_a_channel_field_feed(field_id= 1, 
                                                parameters= {'results': 1})

        sensor_list = {}

        #Checks each sensor is present in thignspeak and if it is create a dict
        #with the field location of the sensor
        for key in s.SENSOR_SET.keys():
            if key.replace('_', ' ') not in ch_feed["channel"].values():
                logger.error('Data sources in the set up not present in thingspeak fields.')
                logger.error(ch_feed["channel"].values())
                logger.error(s.SENSOR_SET.keys())
                logger.error('Exiting...')
                sys.exit()
            else:
                sensor_list[key] = ch_feed["channel"].keys()[ch_feed["channel"].values().index(key.replace('_', ' '))]
     
        logger.debug(sensor_list)

        logger.info('Thingspeak fetch successful.')

    except Exception, e:
        logger.error('Thingspeak fetch failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()


    #---------------------------------------------------------------------------
    # CHECK RRD FILE
    #---------------------------------------------------------------------------
    try:
        rrd = rrd_tools.RrdFile(s.RRDTOOL_RRD_FILE)
        
        if sorted(rrd.ds_list()) != sorted(list(s.SENSOR_SET.keys())):
            logger.error('Data sources in RRD file does not match set up.')
            logger.error(rrd.ds_list())
            logger.error(list(s.SENSOR_SET.keys()))
            logger.error('Exiting...')
            sys.exit()
        else:
            logger.info('RRD fetch successful.')

    except Exception, e:
        logger.error('RRD fetch failed ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        sys.exit()

   
    #---------------------------------------------------------------------------
    # Get last feed upddate from thingspeak
    #---------------------------------------------------------------------------
    last_feed = ts_acc.get_last_entry_in_channel_feed()

    logger.debug('Last TS feed data:')
    logger.debug(last_feed)

    #Thingspeak returns a -1 if there are no records
    if last_feed == '-1':
        last_feed = rrd.last_update()
        
    logger.info('Last TS feed: {last_feed_time}'.format(last_feed_time=last_feed))

   
    #---------------------------------------------------------------------------
    # Fetch values from rrd
    #---------------------------------------------------------------------------
    rrd_entry = rrd.fetch(start= rrd.last_update() - s.UPDATE_RATE)

    rt = collections.namedtuple( 'rt', 'start end step ds value')
    rrd_entry = rt(rrd_entry[0][0], rrd_entry[0][1], rrd_entry[0][2], 
                    rrd_entry[1], rrd_entry[2]) 


    #---------------------------------------------------------------------------
    # Create a list with new thingspeak updates
    #---------------------------------------------------------------------------
    send_list = {}
    for key in s.SENSOR_SET.keys():
        #send_list[sensor_list[key]] = 
        logger.debug(rrd_entry.value[rrd_entry.ds.index(key)])

    logger.debug(send_list)

            
  
    #---------------------------------------------------------------------------
    # Send data to thingspeak
    #---------------------------------------------------------------------------


    #---------------------------------------------------------------------------
    # Check response from update attempt
    #---------------------------------------------------------------------------
            



#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
