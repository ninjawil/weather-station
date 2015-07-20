#-----------------------------------------------------------------------
#
# Controls weatherstation
#
#-----------------------------------------------------------------------

#!usr/bin/env python

#=======================================================================
# Import modules
#=======================================================================
import httplib
import urllib


#=======================================================================
# UPDATE THINGSPEAK CHANNEL
#=======================================================================
def update_channel(host_addr, channel, field_data, screen_output):

    #Create POST data
    data_to_send = {}
    data_to_send['key'] = channel
    for i in range(0, len(field_data)):
        data_to_send['field'+str(i+1)] = field_data[i]

    params = urllib.urlencode(data_to_send)
    headers = {'Content-type': 'application/x-www-form-urlencoded','Accept': 'text/plain'}

    conn = httplib.HTTPConnection(host_addr)
    conn.request('POST', '/update', params, headers)
    response = conn.getresponse()
    
    if screen_output == True:
        print('Data sent to thingspeak: ' + response.reason + '\t status: ' + str(response.status))
    
    data = response.read()
    conn.close()

#===============================================================================
# LOAD THINGSPEAK API KEY
#===============================================================================
def get_write_api_key(filename):

    error_to_catch = getattr(__builtins__,'FileNotFoundError', IOError)
    
    try:
        f = open(filename, 'r')
        
    except error_to_catch:
    
        print('No thingspeak write api key found.')
    
        entry_incorrect = True
        while entry_incorrect:
            api_key = raw_input('Please enter the write key: ')
            answer = raw_input('Is this correct? Y/N >')
            if answer in ('y', 'Y'):
                entry_incorrect = False
    
        with open(filename, 'w') as f:
            f.write(api_key)

    else:
        api_key = f.read()
        print('Thingspeak api key loaded: ' + api_key)
    
    f.close()
    
    return api_key
