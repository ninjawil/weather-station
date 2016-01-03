# ener314rt.py  27/09/2015  D.J.Whale


#!/usr/bin/env python

'''Monitor settings of Energine MiHome plugs'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import time

# Third party modules
import rrdtool
from energenie import OpenHEMS, Devices
from energenie import radio

# Application modules
import log
from Timer import Timer
from messages import MESSAGE_JOIN_ACK, MESSAGE_SWITCH


#===============================================================================
# Trace
#===============================================================================
def trace(msg):

    global logger

    logger.info(str(msg))

log_file = None


#===============================================================================
# Write data to CSV file
#===============================================================================
def updateCSV (msg, log_filename='energenie.csv'):
    HEADINGS = 'timestamp,mfrid,prodid,sensorid,flags,switch,voltage,freq,reactive,real'

    global log_file
    global logger

    if log_file == None:
        if not os.path.isfile(log_filename):
            log_file = open(log_filename, 'w')
            log_file.write(HEADINGS + '\n')
        else:
            log_file = open(log_filename, 'a') # append

    # get the header
    header    = msg['header']
    timestamp = time.time()
    mfrid     = header['mfrid']
    productid = header['productid']
    sensorid  = header['sensorid']

    # set defaults for any data that doesn't appear in this message
    # but build flags so we know which ones this contains
    flags = [0,0,0,0,0]
    switch = None
    voltage = None
    freq = None
    reactive = None
    real = None

    # capture any data that we want
    for rec in msg['recs']:
        paramid = rec['paramid']
        try:
            value = rec['value']
        except:
            value = None
            
        if   paramid == OpenHEMS.PARAM_SWITCH_STATE:
            switch = value
            flags[0] = 1
        elif paramid == OpenHEMS.PARAM_VOLTAGE:
            flags[1] = 1
            voltage = value
        elif paramid == OpenHEMS.PARAM_FREQUENCY:
            flags[2] = 1
            freq = value
        elif paramid == OpenHEMS.PARAM_REACTIVE_POWER:
            flags[3] = 1
            reactive = value
        elif paramid == OpenHEMS.PARAM_REAL_POWER:
            flags[4] = 1
            real = value

    # generate a line of CSV
    flags = "".join([str(a) for a in flags])
    csv = "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (timestamp, mfrid, productid, sensorid, flags, switch, voltage, freq, reactive, real)
    log_file.write(csv + '\n')
    log_file.flush()
    logger.info(csv) # testing



directory = {}

#===============================================================================
# 
#===============================================================================
def allkeys(d):
    result = ""
    for k in d:
        if len(result) != 0:
            result += ','
        result += str(k)
    return result


#===============================================================================
# Update Directory
#===============================================================================    
def updateDirectory(message):

    '''Update the local directory with information about this device'''

    global logger

    now      = time.time()
    header   = message["header"]
    sensorId = header["sensorid"]

    if not directory.has_key(sensorId):
        # new device discovered
        desc = Devices.getDescription(header["mfrid"], header["productid"])
        logger.info("ADD device:%s %s" % (hex(sensorId), desc))
        directory[sensorId] = {"header": message["header"]}
        logger.info(allkeys(directory))

    directory[sensorId]["time"] = now
    #TODO would be good to keep recs, but need to iterate through all and key by paramid,
    #not as a list index, else merging will be hard.




#===============================================================================
# Grab data
#===============================================================================
def monitor():

    '''Send discovery and monitor messages, and capture any responses'''

    # logger = logging.getLogger('root')
    global logger

    # Define the schedule of message polling
    sendSwitchTimer    = Timer(60, 1)   # every n seconds offset by initial 1
    switch_state       = 0             # OFF
    radio.receiver()
    decoded            = None
    message_not_received = True

    while message_not_received:
        # See if there is a payload, and if there is, process it
        if radio.isReceiveWaiting():
            trace("receiving payload")
            payload = radio.receive()
            message_not_received = False
            try:
                decoded = OpenHEMS.decode(payload)
            except OpenHEMS.OpenHEMSException as e:
                logger.error("Can't decode payload:" + str(e))
                message_not_received = True
                continue
                      
            #OpenHEMS.showMessage(decoded)
            updateDirectory(decoded)
            updateCSV(decoded)
            
            #TODO: Should remember report time of each device,
            #and reschedule command messages to avoid their transmit slot
            #making it less likely to miss an incoming message due to
            #the radio being in transmit mode

            # assume only 1 rec in a join, for now
            if len(decoded["recs"])>0 and decoded["recs"][0]["paramid"] == OpenHEMS.PARAM_JOIN:
                #TODO: write OpenHEMS.getFromMessage("header_mfrid")
                response = OpenHEMS.alterMessage(MESSAGE_JOIN_ACK,
                    header_mfrid=decoded["header"]["mfrid"],
                    header_productid=decoded["header"]["productid"],
                    header_sensorid=decoded["header"]["sensorid"])
                p = OpenHEMS.encode(response)
                radio.transmitter()
                radio.transmit(p)
                radio.receiver()

        if sendSwitchTimer.check() and decoded != None and decoded["header"]["productid"] in [Devices.PRODUCTID_C1_MONITOR, Devices.PRODUCTID_R1_MONITOR_AND_CONTROL]:
            request = OpenHEMS.alterMessage(MESSAGE_SWITCH,
                header_sensorid=decoded["header"]["sensorid"],
                recs_0_value=switch_state)
            p = OpenHEMS.encode(request)
            radio.transmitter()
            radio.transmit(p)
            radio.receiver()
            switch_state = (switch_state+1) % 2 # toggle
        


#===============================================================================
# MAIN
#===============================================================================
def main():
   
    '''Entry point for script'''

    script_name = os.path.basename(sys.argv[0])

    #---------------------------------------------------------------------------
    # Set up logger
    #---------------------------------------------------------------------------
    global logger

    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                        folder= '/home/pi/python/pyenergenie-master',
                                        script= script_name[:-3]))

    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name)) 
    

    #---------------------------------------------------------------------------
    # Set up radio
    #---------------------------------------------------------------------------
    radio.init()
    OpenHEMS.init(Devices.CRYPT_PID)

    try:
        monitor()

    finally:
        radio.finished()



#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()
