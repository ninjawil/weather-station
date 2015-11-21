#-------------------------------------------------------------------------------
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

#!/usr/bin/env python

'''Manages RRD export to XML'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import subprocess
import shlex

# Third party modules
import rrdtool

# Application modules
import log
import settings as s




#===============================================================================
# Export RRD data to xml
#===============================================================================
def rrdExport(start , step , sortieXML):
    texte = "rrdtool xport -s {0} -e now --step {1} ".format(start, step)
    texte += "DEF:a={0}:inside_temp:AVERAGE ".format(s.RRDTOOL_RRD_FILE)
    texte += "DEF:b={0}:inside_hum:AVERAGE ".format(s.RRDTOOL_RRD_FILE)
    texte += "DEF:c={0}:door_open:AVERAGE ".format(s.RRDTOOL_RRD_FILE)
    texte += "DEF:d={0}:precip_rate:AVERAGE ".format(s.RRDTOOL_RRD_FILE)
    texte += "DEF:e={0}:precip_acc:AVERAGE ".format(s.RRDTOOL_RRD_FILE)
    texte += "DEF:f={0}:outside_temp:AVERAGE ".format(s.RRDTOOL_RRD_FILE)  
    texte += "XPORT:a:""inside_temp"" "
    texte += "XPORT:b:""inside_hum"" "
    texte += "XPORT:c:""door_open"" "
    texte += "XPORT:d:""precip_rate"" "
    texte += "XPORT:e:""precip_acc"" "
    texte += "XPORT:f:""outside_temp"" "


    fileout = open("/home/pi/weather/data/"+sortieXML,"w")
    args = shlex.split(texte)
    subprocess.Popen(args, stdout=fileout)
    fileout.close()



#===============================================================================
# MAIN
#===============================================================================
def main():
    
    '''Entry point for script'''

    # ok extact 3 hours data
    rrdExport("now-3h",300, "weather3h.xml")

    #ok 24 hours
    rrdExport("now-24h",900, "weather24h.xml")

    #ok 48 hours
    rrdExport("now-48h",1800, "weather48h.xml")

    #ok 1 week
    rrdExport("now-8d",3600, "weather1w.xml")

    #ok 1 month
    rrdExport("now-1month",14400, "weather1m.xml")

    #ok 3 month
    rrdExport("now-3month",28800, "weather3m.xml")

    #ok 1 year
    rrdExport("now-1y",43200, "weather1y.xml")


#===============================================================================
# BOILER PLATE
#===============================================================================
if __name__=='__main__':
    sys.exit(main())
