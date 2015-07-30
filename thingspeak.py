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


class ThingspeakAcc():
    
    '''Sets up thingspeak accounts'''
    
    def __init__(self, acc_host_addr, key_file):
        self.host_addr = acc_host_addr
        self.api_key = get_write_api_key(key_file)
        
        
    #===================================================================
    # UPDATE THINGSPEAK CHANNEL
    #===================================================================
    def update_channel(field_data):
        
        #Create POST data
        data_to_send = {}
        data_to_send['key'] = self.api_key
        
        for i in range(0, len(field_data)):
            ata_to_send['field'+str(i+1)] = field_data[i]
            
        params = urllib.urlencode(data_to_send)
        headers = {'Content-type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/plain'}
                    
        conn = httplib.HTTPConnection(self.host_addr)
        conn.request('POST', '/update', params, headers)
        response = conn.getresponse()

        data = response.read()
        conn.close()
        
        return response


    #===========================================================================
    # LOAD THINGSPEAK API KEY
    #===========================================================================
    def get_write_api_key(filename):
    
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
            with open(filename, 'w') as f:
                f.write(key)
        else:
            key = f.read()
            print('Thingspeak api key loaded: ' + key)
        
        f.close()
        
        return key
