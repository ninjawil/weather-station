#-----------------------------------------------------------------------
#
# Controls weatherstation
#
#-----------------------------------------------------------------------

#!usr/bin/env python

#=======================================================================
# Import modules
#=======================================================================
import httplib, urllib


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
