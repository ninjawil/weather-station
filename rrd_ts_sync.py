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
import settings as s
import rrdtool
import thingspeak



#===============================================================================
# MAIN
#===============================================================================
def main():

    # --- Set up thingspeak account ---
    #Set up inital values for variables
    thingspeak_write_api_key     = ''
        
    #Set up thingspeak account
    thingspeak_acc = thingspeak.ThingspeakAcc(s.THINGSPEAK_HOST_ADDR,
                                                s.THINGSPEAK_API_KEY_FILENAME,
                                                s.THINGSPEAK_CHANNEL_ID)

    #Create RRD files if none exist
    if not os.path.exists(s.RRDTOOL_RRD_FILE):
            return

    # ========== Timed Loop ==========
    try:
        while True:
       
            #Fetch values from rrd
            data_values = rrdtool.fetch(s.RRDTOOL_RRD_FILE, 'LAST', 
                                        '-s', str(s.UPDATE_RATE * -2))
  
            # --- Send data to thingspeak ---
            #Create dictionary with field as key and value
            sensor_data = {}
            for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
                sensor_data[value[s.TS_FIELD]] = value[s.VALUE]
            response = thingspeak_acc.update_channel(sensor_data)


    # ========== User exit command ==========
    except KeyboardInterrupt:
        sys.exit(0)
            

#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
