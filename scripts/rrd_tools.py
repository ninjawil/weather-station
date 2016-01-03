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

'''Manages RRD file'''


#===============================================================================
# Import modules
#===============================================================================

# Standard Library
import os
import logging
import collections
import subprocess

# Third party modules
import rrdtool


#===============================================================================
class RrdFile:
 
    '''Sets up the RRD file '''
 
    def __init__(self, filename):
        self.file_name = filename
        self.logger = logging.getLogger('root')
 
 
    #---------------------------------------------------------------------------
    # CREATE RRD FILE
    #---------------------------------------------------------------------------
    def create_file(self, sensor_set, rra_set, update_rate, heartbeat, start_time):
        
        '''Creates a RRD file based on a dictionary of sensor settings, and a list
        of RRA file settings.'''
        
        ss = collections.namedtuple('ss', 'enable ref unit min max type')
        sensor = {k: ss(*sensor_set[k]) for k in sensor_set}

        rd = collections.namedtuple('ss', 'cf res period')
        rra = {k: rd(*rra_set[k]) for k in rra_set}

        #Prepare RRD set
        rrd_set = [self.file_name, 
                    '--step', '{step}'.format(step=update_rate), 
                    '--start', '{start_t:.0f}'.format(start_t=start_time)]
                    
        #Prepare data sources
        rrd_set += ['DS:{ds_name}:{ds_type}:{ds_hb}:{ds_min}:{ds_max}'.format(
                                    ds_name=i,
                                    ds_type=sensor[i].type,
                                    ds_hb=str(heartbeat*update_rate),
                                    ds_min=sensor[i].min,
                                    ds_max=sensor[i].max) 
                        for i in sorted(sensor)]

        #Prepare RRA files
        rrd_set += ['RRA:{cf}:0.5:{steps}:{rows}'.format(
                                    cf=rra[i].cf,
                                    steps=str((rra[i].res*60)/update_rate),
                                    rows=str((rra[i].period*24*60)/rra_set[i+1]))
                        for i in sorted(rra)]

        self.logger.debug(rrd_set)

        rrdtool.create(rrd_set)

        return rrd_set


    #---------------------------------------------------------------------------
    # UPDATE RRD FILE
    #---------------------------------------------------------------------------
    def update_file(self, timestamp='N', ds_name=None, values=None):

        '''Runs an rrd update from a list of values and a time since epoch time
        stamp. Returns an OK or an error value if unsuccesful.'''

        self.logger.debug('-t{ds}, {update_time}:{data}'.format(
                ds= ':'.join(ds_name),
                update_time= str(timestamp),
                data= ':'.join(map(str, values))))

        try:
            if ds_name and values:
                rrdtool.update(self.file_name, 
                                '-t{ds}'.format(ds= ':'.join(ds_name)),
                                '{update_time}:{data}'.format(
                                                update_time= str(timestamp),
                                                data= ':'.join(map(str, values))))
                return 'OK'

        except rrdtool.error, e:
            self.logger.error('RRDtool update FAIL ({error_v})'.format(error_v= e))
            return e


    #---------------------------------------------------------------------------
    # INFO
    #---------------------------------------------------------------------------
    def info(self):
        '''Provides rrdinfo command'''
        return rrdtool.info(self.file_name)


    #---------------------------------------------------------------------------
    # DS LIST
    #---------------------------------------------------------------------------
    def ds_list(self):
        '''Returns a list of data sources'''        
        return self.fetch()[1]


    #---------------------------------------------------------------------------
    # LAST UPDATE
    #---------------------------------------------------------------------------
    def last_update(self):
        '''Returns the time of the last update'''
        return self.info()['last_update']


    #---------------------------------------------------------------------------
    # NEXT UPDATE
    #---------------------------------------------------------------------------
    def next_update(self, cf='LAST'):
        '''Returns the time for the next update'''
        return self.fetch(cf=cf)[0][1]


    #---------------------------------------------------------------------------
    # FETCH
    #---------------------------------------------------------------------------
    def fetch(self, cf='LAST', start='now', end='now'):
        '''Returns the result of an rrdfetch command'''
        data = rrdtool.fetch(self.file_name, cf, '-s', str(start), '-e', str(end))
        self.logger.debug(
            'RRDtool fetch value cf={cf_} start={start_t} end={end_t}:'.format(
                                        cf_=cf, 
                                        start_t= start, 
                                        end_t= end))
        self.logger.debug(data)
        return data


    #---------------------------------------------------------------------------
    # EXPORT
    #---------------------------------------------------------------------------
    def export(self, start='-1d', end='now', step='300', ds_list=None, 
                output_file=None, cf='LAST'):
        '''Exports RRD to XML'''

        try:
            if ds_list:
                exp_cmd = ['rrdtool','xport',
                           '-s', '{start_t}'.format(start_t=start),
                           '-e', '{end_t}'.format(end_t=end),
                           '--step', '{res}'.format(res= step)]

                exp_cmd += ['DEF:{vname}={rrd_file}:{ds_name}:{cons}'.format(
                                                            vname= ds,
                                                            rrd_file=self.file_name,
                                                            ds_name= ds,
                                                            cons= cf)
                            for ds in sorted(ds_list)]

                exp_cmd += ['XPORT:{vname}:{ds_name}'.format(vname= ds, ds_name= ds)
                            for ds in sorted(ds_list)]


                # !!!!!!!!!!!!!!!!
                # No binding for xport on python-rrdtool 1.4.7
                # exp_cmd has 'rrdtool','xport' added to run it from subprocess
                # rrdtool.xport(exp_cmd)
                # !!!!!!!!!!!!!!!!

                self.logger.debug(' '.join(exp_cmd))
                fileout = open(output_file,"w")
                subprocess.Popen(exp_cmd, stdout=fileout)
                fileout.close()

                return 'OK'

        except ValueError, e:
            self.logger.critical('RRDtool export FAIL ({error_v})'.format(error_v= e))
            return e



