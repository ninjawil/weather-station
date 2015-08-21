#-----------------------------------------------------------------------
#
# Interfaces to thingspeak
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
#-----------------------------------------------------------------------

#!usr/bin/env python

#=======================================================================
# Import modules
#=======================================================================
import httplib
import urllib
import time


class ThingspeakAcc():
    
    '''Sets up thingspeak accounts -
    + Write api key can be either the api key or a filename with extension '.txt' with the api key inside'''
    
    def __init__(self, acc_host_addr, write_api_key, acc_channel_id):
        self.host_addr = acc_host_addr
        self.channel_id = acc_channel_id
        
        if(write_api_key[-4:] == '.txt'):
            self.api_key = self.get_write_api_key(write_api_key)
        else:
            self.api_key = write_api_key
            write_api_key_file(filename)
        

    #===================================================================
    # PREPARE HEADERS
    #===================================================================
    def prepare_connection(self, parameters):
        
        #Create POST data
        if 'api_key' not in parameters.keys()
            parameters['key'] = self.api_key
   
        params = urllib.urlencode(parameters)

        headers = {'Content-type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/plain'}
                    
        conn = httplib.HTTPConnection(self.host_addr)
    

    #===================================================================
    # UPDATE THINGSPEAK CHANNEL
    #===================================================================
    def update_channel(self, parameters):
        
        '''Valid parameters:
            api_key (string) - Write API Key for this specific Channel (required). 
                                The Write API Key can optionally be sent via a THINGSPEAKAPIKEY HTTP header.
            field1 (string) - Field 1 data (optional)
            field2 (string) - Field 2 data (optional)
            field3 (string) - Field 3 data (optional)
            field4 (string) - Field 4 data (optional)
            field5 (string) - Field 5 data (optional)
            field6 (string) - Field 6 data (optional)
            field7 (string) - Field 7 data (optional)
            field8 (string) - Field 8 data (optional)
            lat (decimal) - Latitude in degrees (optional)
            long (decimal) - Longitude in degrees (optional)
            elevation (integer) - Elevation in meters (optional)
            status (string) - Status update message (optional)
            twitter (string) - Twitter username linked to ThingTweet (optional)
            tweet (string) - Twitter status update; see updating ThingTweet for more info (optional)
            created_at (datetime) - Date when this feed entry was created, in ISO 8601 format, 
            for example: 2014-12-31 23:59:59 . Time zones can be specified via the timezone parameter (optional)'''
        
        prepare_connection(parameters)
        
        conn.request('POST', '/update', params, headers)
        response = conn.getresponse()

        data = response.read()
        conn.close()
        
        return response


    #===================================================================
    # GET CHANNEL FEED
    #===================================================================
    def get_channel_feed(self, parameters):
        
        '''Valid parameters:
                api_key (string) Read API Key for this specific Channel 
                    (optional--no key required for public channels)
                results (integer) Number of entries to retrieve, 8000 max, default of 100 (optional)
                days (integer) Number of 24-hour periods before now to include in feed (optional)
                start (datetime) Start date in format YYYY-MM-DD%20HH:NN:SS (optional)
                end (datetime) End date in format YYYY-MM-DD%20HH:NN:SS (optional)
                timezone (string) Timezone identifier for this request (optional)
                offset (integer) Timezone offset that results should be displayed in. 
                    Please use the timezone parameter for greater accuracy. (optional)
                status (true/false) Include status updates in feed by setting "status=true" (optional)
                metadata (true/false) Include Channel's metadata by setting "metadata=true" (optional)
                location (true/false) Include latitude, longitude, 
                    and elevation in feed by setting "location=true" (optional)
                min (decimal) Minimum value to include in response (optional)
                max (decimal) Maximum value to include in response (optional)
                round (integer) Round to this many decimal places (optional)
                timescale (integer or string) Get first value in this many minutes, 
                    valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily" (optional)
                sum (integer or string) Get sum of this many minutes, 
                    valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily" (optional)
                average (integer or string) Get average of this many minutes, 
                    valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily" (optional)
                median (integer or string) Get median of this many minutes, 
                    valid values: 10, 15, 20, 30, 60, 240, 720, 1440, "daily" (optional)
                callback (string) Function name to be used for JSONP cross-domain requests (optional)'''
                
        prepare_connection(parameters)
        conn.request('GET', '/channels/' + self.channel_id + '/feeds/', params, headers)
        response = conn.getresponse()

        data = response.read()
        conn.close()
        
        return response 


    #===================================================================
    # GET LAST FEED
    #===================================================================
    def get_last_entry in channel_feed(self, parameters):
        
        '''Valid parameters:
            api_key (string) Read API Key for this specific Channel 
                (optional--no key required for public channels)
            timezone (string) Timezone identifier for this request (optional)
            offset (integer) Timezone offset that results should be displayed in. 
                Please use the timezone parameter for greater accuracy. (optional)
            status (true/false) Include status updates in feed by setting "status=true" (optional)
            location (true/false) Include latitude, longitude, 
                and elevation in feed by setting "location=true" (optional)
            callback (string) Function name to be used for JSONP cross-domain requests (optional)
            prepend (string) Text to add before the API response (optional)
            append (string) Text to add after the API response (optional)'''
        
        prepare_connection(parameters)
        conn.request('GET', '/channels/' + self.channel_id + '/feeds/last', params, headers)
        response = conn.getresponse()

        data = response.read()
        conn.close()
        
        #Convert created at time to seconds since epoch
        feed_time = time.strptime(response['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        response['created_at'] = time.mktime(feed_time)
        
        return response


    #===========================================================================
    # WRITE API KEY TO FILE
    #===========================================================================
    def write_api_key_file(self, filename):
        with open(filename, 'w') as f:
                f.write(key)

    
    #===========================================================================
    # LOAD THINGSPEAK API KEY
    #===========================================================================
    def get_write_api_key(self, filename):
    
        error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
        
        try:
            f = open(filename, 'r')
        except error_to_catch:
            print('No thingspeak write api key found.')
            entry_incorrect = True
            while entry_incorrect:
                key = raw_input('Please enter the write key: ')
                answer = raw_input('Is this correct? Y/N >')
                if answer in ('y', 'Y'):
                    entry_incorrect = False
            write_api_key_file(filename)
        else:
            key = f.read()
        
        f.close()
        
        return key
