#-------------------------------------------------------------------------------
#
# 'Controls shed weather station
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

'''Manages RRD file'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import sys
import time
import datetime
import logging

# Third party modules
import rrdtool



#===============================================================================
# CREATE RRD FILE
#===============================================================================
def create_rrd_file(file_dir, file_name, sensor_set, rra_set, update_rate, 
                    heartbeat, start_time):
    
    '''Creates a RRD file'''

    #Check if directory exists
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    #Prepare data sources
    rrd_ds      = []
    for i in sorted(sensor_set):
        rrd_ds.append('DS:{ds_name}:{ds_type}:{ds_hb}:{ds_min}:{ds_max}'.format(
                                ds_name=i,
                                ds_type=sensor_set[i][5],
                                ds_hb=str(heartbeat*update_rate),
                                ds_min=sensor_set[i][3],
                                ds_max=sensor_set[i][4]))

    #Prepare RRA files
    rra_files   = []
    for i in range(0,len(rra_set),3):
        rra_files.append('RRA:{cf}:0.5:{steps}:{rows}'.format(
                                cf=rra_set[i],
                                steps=str((rra_set[i+1]*60)/update_rate),
                                rows=str(((rra_set[i+2])*24*60)/rra_set[i+1])))

    #Prepare RRD set
    rrd_set = []
    rrd_set = [file_name, 
                '--step', '{step}'.format(step=update_rate), 
                '--start', '{start_t:.0f}'.format(start_t=start_time)]
    rrd_set +=  rrd_ds + rra_files

    rrdtool.create(rrd_set)

    return rrd_set


#===============================================================================
# UPDATE RRD FILE
#===============================================================================
def update_rrd_file(file_name,data_values):
    try:
        rrdtool.update(file_name, 'N:{values}'.format(
                values=':'.join([str(data_values[i]) for i in sorted(data_values)]))
        e= 'OK'
    except rrdtool.error, e:
        continue

    return e
