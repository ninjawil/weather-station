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
from xml.etree import cElementTree as ET

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
                                    cf=rra[key].cf,
                                    steps=str(int((rra[key].res*60)/update_rate)),
                                    rows=str(int((rra[key].period*24*60)/rra[key].res)))
                        for key in sorted(rra)]

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
    # CHECK FILE
    #---------------------------------------------------------------------------
    def check_ds_list_match(self, sensor_list):

        try:
            list_in_file = self.ds_list()

            if sorted(list_in_file) != sorted(sensor_list):
                self.logger.error('Data sources in RRD file does not match set up.')
                self.logger.error(list_in_file)
                self.logger.error(sensor_list)
                self.logger.error('Exiting...')
                return False
            else:
                self.logger.info('RRD fetch successful.')
                return True

        except Exception, e:
            self.logger.error('RRD fetch failed ({error_v}). Exiting...'.format(
                error_v=e))
            return False


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
    def fetch(self, cf='LAST', start='now', end='now', res=''):
        '''Returns the result of an rrdfetch command'''
        if res == '':
            data = rrdtool.fetch(self.file_name, cf, '-s', str(start), '-e', str(end))
        else:
            data = rrdtool.fetch(self.file_name, cf, '-s', str(start), '-e', str(end), '-r', str(res))
        self.logger.debug(
            'RRDtool fetch value cf={cf_} start={start_t} end={end_t} res={res_}:'.format(
                                        cf_=cf, 
                                        start_t= start, 
                                        end_t= end,
                                        res_=res))
        self.logger.debug(data)
        return data


    #---------------------------------------------------------------------------
    # FETCH LIST
    #---------------------------------------------------------------------------
    def fetch_list(self, consolidation, data, days=7):
        '''
        Fetches previous days values from rrd and returns it as a list.

        Any NaN values are ignored and not included in the list.
        '''

        rrd_entry = self.fetch(  cf= consolidation, 
                                start='e-{t}d'.format(t=days-1), 
                                end='-1d', 
                                res='86400')
            
        rt = collections.namedtuple( 'rt', 'start end step ds value')
        rrd_entry = rt(rrd_entry[0][0], rrd_entry[0][1], rrd_entry[0][2], 
                            rrd_entry[1], rrd_entry[2]) 

        data_length = len(rrd_entry.value)

        return [rrd_entry.value[i][rrd_entry.ds.index(data)] 
                    for i in range(0,data_length) if rrd_entry.value[i][rrd_entry.ds.index(data)] is not None]


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


#===============================================================================
# Misc functions
#===============================================================================


#---------------------------------------------------------------------------
# CREATE DICTIONARY FROM XML FILE
#---------------------------------------------------------------------------
def xml_to_dict(filename):
    '''Converts a RRD exported XML file to dictionary format'''

    logger = logging.getLogger('root')

    logger.debug('Exporting {f1} to dict'.format(f1=filename))
    
    try:
        xml = ET.ElementTree(file=filename)  
        root = xml.getroot()
        xml_dict = {'meta': {}, 'data': {}}

        # Fill in meta data
        for elem in root.find('meta'):
            if elem:
                xml_dict['meta'][elem.tag] = [i.text for i in elem]
            elif elem.text:
                xml_dict['meta'][elem.tag] = int(elem.text)

        # Grab data from xml and add to dictionary with keys from source name
        no_of_sources = len(xml_dict['meta']['legend'])
        xml_dict['data'] = {int(elem[0].text): [elem[i+1].text for i in xrange(no_of_sources)] for elem in xml.find('data')}

        return xml_dict

    except ValueError, e:
        logger.error('Export FAIL ({error_v})'.format(error_v= e))
        return


#---------------------------------------------------------------------------
# COMBINE THREE XML FILES (AVG, MAX, MIN)
#---------------------------------------------------------------------------
def avg_max_min_to_xml(xml_max, xml_min, xml_avg, output_xml):
    '''Exports a single XML file from three sepparate XML files
    with AVERAGE, MAX, MIN values'''

    logger = logging.getLogger('root')

    logger.debug('Combining XML files')

    try:
        # Grab data from xml files into dictionary
        data = {'avg': xml_to_dict(xml_avg),
                'min': xml_to_dict(xml_min),
                'max': xml_to_dict(xml_max)}

        # Check is resolution is the same on all files
        step = data['avg']['meta']['step']
        if  data['min']['meta']['step'] == step and data['max']['meta']['step'] == step:
                
            # Change sensor names to reflect Min or Max values
            data['min']['meta']['legend'] = [ s + '_min' for s in data['min']['meta']['legend']]
            data['max']['meta']['legend'] = [ s + '_max' for s in data['max']['meta']['legend']]

            # Create output dictionary and populate with a list of all unique sensors 
            out_data = {'meta': {'legend': sorted(set(s for k in data for s in data[k]['meta']['legend']))},
                        'data': {}}

            # Create a unique list of timestamps from all 3 files
            times = sorted(set(t for f in data for t in data[f]['data']))

            # Loop for each uniquetime stamp (create if missing), create a list of NaN,
            # and then populate if data is available
            no_of_sources = len(out_data['meta']['legend'])
            out_data['data'] = {t: ['NaN'] * no_of_sources for t in xrange(times[0], times[-1] + step, step)}
            for k in data:
                for sensor in data[k]['meta']['legend']:
                    data_out_loc = out_data['meta']['legend'].index(sensor)
                    data_loc = data[k]['meta']['legend'].index(sensor)
                    for t in data[k]['data']:
                        out_data['data'][t][data_out_loc] = data[k]['data'][t][data_loc]
          
            # Update Legend list
            out_data['meta']['start'] =     times[0]
            out_data['meta']['step'] =      step
            out_data['meta']['end'] =       times[-1]
            out_data['meta']['columns'] =   no_of_sources
            out_data['meta']['rows'] =      len(out_data['data'].keys())
            
        dict_to_xml(output_xml, out_data)
    
    except ValueError, e:
        logger.error('Combine XML files FAIL ({error_v})'.format(error_v= e))
        return

#---------------------------------------------------------------------------
# INDENT XML FILE
#---------------------------------------------------------------------------
def indent(elem, level=0):
    i = "\n" + level * "  "
    j = "\n" + (level-1)*"  "
    if len(elem) and elem.tag is not 'row':
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    return elem


#---------------------------------------------------------------------------
# CREATE XML FILE FROM DICTIONARY
#---------------------------------------------------------------------------
def dict_to_xml(output_xml, data_dict):
    ''' Create an xml file from a dictionary of data'''


    logger = logging.getLogger('root')

    logger.debug('Generating XML file from dictionary')

    try:
        root = ET.Element('xport')

        # Write meta data
        meta = ET.SubElement(root, 'meta')
        for i in ['start', 'step', 'end', 'rows', 'columns', 'legend']:
            child = ET.SubElement(meta, i)
            if isinstance(data_dict['meta'][i], list):
                item_length = len(data_dict['meta'][i])
                for j in xrange(item_length):
                    childchild = ET.SubElement(child, 'entry')
                    childchild.text = str(data_dict['meta'][i][j])
            else:
                child.text = str(data_dict['meta'][i])
                    
        # Add time and values to XML set up
        data = ET.SubElement(root, 'data')
        for t in sorted(list(data_dict['data'].keys())):
            row = ET.SubElement(data, 'row')
            time = ET.SubElement(row, 't')
            time.text = str(t)
            for v in data_dict['data'][t]:
                value = ET.SubElement(row, 'v')
                value.text = str(v) 

        # Prettify data and write it to file
        tree = ET.ElementTree(indent(root))
        tree.write(output_xml, encoding='utf-8')

    except ValueError, e:
        logger.error('XML creation FAIL ({error_v})'.format(error_v= e))
        return
