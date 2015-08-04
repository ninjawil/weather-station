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
import os
import settings as s


#===============================================================================
# DRAW HELP MENU
#===============================================================================
def help_menu():
    print('usage: ./wstation.py {command}')
    print('')
    print('   --outsensor=OFF    ',
          '- disables outside temperature monitoring')
    print('   --insensor=OFF     ',
          '- disables inside temperature monitoring')
    print('   --rainsensor=OFF   ',
          '- disables rainfall monitoring')
    print('   --thingspeak=OFF   ',
          '- disable update to ThingSpeak')
    print('   --rrdtool=OFF   ',
          '- disable round robin database')
    print('   --quiet            ',
          '- outputs data to screen')


#===============================================================================
# DRAW SCREEN
#===============================================================================
def draw_screen(sensors, thingspeak_enable, key, rrd_enable, rrd_set):
    
    os.system('clear')
    
    display_string = []
    
    display_string.append('WEATHER STATION')
    display_string.append('')
    display_string.append('Next precip. acc. reset at '+ str(s.PRECIP_ACC_RESET_TIME))

    #Display thingspeak field data set up
    if thingspeak_enable:
        display_string.append('')
        display_string.append('Thingspeak write api key: '+key)
        display_string.append('')
        display_string.append('Thingspeak field set up:')
        display_string.append('  Field\tName\t\tValue\tUnit')
        display_string.append('  ---------------------------------------')
        for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
            display_string.append('  ' + str(value[s.TS_FIELD]) + '\t' + key + 
                                    '\t' + str(value[s.VALUE]) + '\t' + value[s.UNIT])
    
    #Display RRDtool set up
    if rrd_enable:
        #rrd display header
        display_string.append('')
        display_string.append('RRDtool set up:')
        
        #Work out shortest list
        if len(rrd_set[0]) < len(rrd_set[1]):
            short_list_ref = 0
        else:
            short_list_ref = 1

        #Make lists equal in length
        size_difference = len(rrd_set[not short_list_ref]) - len(rrd_set[short_list_ref])
        rrd_set[short_list_ref].extend([''] * size_difference)
        
        #Merge lists
        display_string += ['t'+x+'\t\t'+y for x,y in zip(rrd_set[0], rrd_set[1])]
        display_string.append('')

    #Create table header
    display_string.append('')
    header ='Date\t\tTime\t\t'
    header_names = ''
    for key, value in sorted(sensors.items(), key=lambda e: e[1][0]):
        header_names = header_names + key +'\t'
    header = header + header_names + 'TS Send'
    display_string.append(header)
    display_string.append('=' * (len(header) + 5 * header.count('\t')))
 
    #Find the total number of rows on screen
    rows, columns = os.popen('stty size', 'r').read().split()
    
    #Draw screen
    print('\n'.join(display_string))
    
    #Return number of rows left for data
    return(int(rows) - len(display_string))

