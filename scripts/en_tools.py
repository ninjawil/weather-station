#!usr/bin/env python

#===============================================================================
# Import modules
#===============================================================================
# Standard Library
import os
import sys
import datetime
import time
import json
import getopt
import collections
import csv

# Third party modules
import hashlib
import binascii
import evernote.edam.notestore.NoteStore as NoteStore
import evernote.edam.userstore.constants as UserStoreConstants
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors
from evernote.api.client import EvernoteClient

# Application modules
import settings as s
import log
import logging
import check_process
# import watchdog as wd


#---------------------------------------------------------------------------
# Get guid for tag
#---------------------------------------------------------------------------
def get_guid(items, search_string):
    '''
    Function returns the guid from a evernote list

    items           Struct: List item as defined by Evernote
    search_string   string of tag name to search 

    '''

    return {item.guid: item.name for item in items if item.name.find(search_string) > -1}

#---------------------------------------------------------------------------
# Get all children from parent tag
#---------------------------------------------------------------------------
def get_tag_children(tag_list, parent_guid):
    '''
    Function returns all children from the tag guid provided

    tag_list        Struct: Tag as defined by Evernote
    search_string   string of tag name to search 

    '''

    return {tag.guid: tag.name for tag in tag_list if tag.parentGuid == parent_guid}


#---------------------------------------------------------------------------
# Get date from ISO week
#---------------------------------------------------------------------------
def get_thrs_date_from_iso_week(date_str):
    '''
    Function returns date of the Thursday of the week passed

    https://stackoverflow.com/questions/5882405/get-date-from-iso-week-number-in-python

    Thanks to Uwe Kleine-Konig
    '''
    ret = datetime.datetime.strptime(date_str + '-4', "%Y-W%W-%w")
    if datetime.date(int(ret.year), 1, 4).isoweekday() > 4:
        ret -= datetime.timedelta(days=7)
    return ret


#---------------------------------------------------------------------------
 # Check state tags file is correct and up to date
#---------------------------------------------------------------------------
def check_state_tags(tag_list, filename):
    '''
    Function checks states in state tag file is up to date

    tag_list        State tags from evernote
    filename        State tag JSON file

    '''

    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = logging.getLogger('root')


    #---------------------------------------------------------------------------
    # GET DATA FROM FILE
    #---------------------------------------------------------------------------
    try:
        with open(filename, 'r') as f:
            state_config = json.load(f)

    except Exception, e:
        logger.warning('Warning ({error_v}).'.format(error_v=e), exc_info=True)
        state_config = {}


    #---------------------------------------------------------------------------
    # CHECK & SORT DATA
    #---------------------------------------------------------------------------    
    tag_by_name_cfg_file = {values['name']: key for key, values in state_config.items()}

    for guid, name in tag_list.items():

        if guid in state_config.keys():
            if name not in state_config[guid]['name']:
                state_config[guid]['name'] = name             
            continue

        if name in tag_by_name_cfg_file.keys():
            state_config[guid] = state_config[tag_by_name_cfg_file[name]]
            del state_config[tag_by_name_cfg_file[name]]
            continue                

        state_config[guid] = {
            "color":    "",
            "name":     name,
            "symbol":   "",
            "event":    ""
        }

    #---------------------------------------------------------------------------
    # WRITE DATA TO FILE
    #---------------------------------------------------------------------------
    with open(filename, 'w') as f:
        json.dump(state_config, f)

    logger.debug('Writting state configuration to file: COMPLETE')


    return state_config


#===============================================================================
class EvernoteAcc:
 
    #---------------------------------------------------------------------------
    # Sets up the Evernote Account 
    #--------------------------------------------------------------------------- 
    def __init__(self, key, config, sand_box= False):

        self.key    = key     
        self.logger = logging.getLogger('root')
        self.cfg    = { 
            "gardening_tag":    config['evernote']['GARDENING_TAG'],
            "notebook":         config['evernote']['NOTEBOOK'],
            "plant_tag_id":     config['evernote']['PLANT_TAG_ID'],
            "location_tag_id":  config['evernote']['LOCATION_TAG_ID'],
            "state_tag_id":     config['evernote']['STATE_TAG_ID'],
            "plant_no_id":      '+plants', #config['evernote']['PLANT_NO_TAG_ID'],
            "sand_box":         sand_box, 
            "force_sync":       False
        }

        #------------------------------------------------------------------------
        # Get Account Info
        #------------------------------------------------------------------------
        client = EvernoteClient(token=self.key['AUTH_TOKEN'], sandbox=sand_box)
        self.note_store  = client.get_note_store()
        self.user_store  = client.get_user_store()

        #------------------------------------------------------------------------
        # Check evernote API
        #------------------------------------------------------------------------
        version_ok = self.user_store.checkVersion(
            "Evernote EDAMTest (Python)",
            UserStoreConstants.EDAM_VERSION_MAJOR,
            UserStoreConstants.EDAM_VERSION_MINOR)

        if not version_ok:
            self.logger.warning("Evernote API version is not up to date.")



    #---------------------------------------------------------------------------
    # Get evernote data
    #---------------------------------------------------------------------------
    def new_entry(self, note_data):
        '''
        Function gets evernote data and updates gardening JSON file.
        Taken from evernote developers page and slightly adapted for this function.

        '''

        nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
        nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
        nBody += "<en-note>%s</en-note>" % note_data['body']

        ## Create note object
        ourNote = Types.Note()
        ourNote.title       = note_data['title']
        ourNote.content     = nBody 
        ourNote.created     = note_data['created'] 
        ourNote.tagNames    = note_data['tags']

        # ## parentNotebook is optional; if omitted, default notebook is used
        # if note_data['notebook'] and hasattr(note_data['notebook'], 'guid'):
        #     ourNote.notebookGuid = parentNotebook.guid

        ## Attempt to create note in Evernote account
        try:
            note = self.note_store.createNote(self.key['AUTH_TOKEN'], ourNote)
            self.logger.info('Note Created')
        except Errors.EDAMUserException, edue:
            ## Something was wrong with the note data
            ## See EDAMErrorCode enumeration for error code explanation
            ## http://dev.evernote.com/documentation/reference/Errors.html#Enum_EDAMErrorCode
            self.logger.error("EDAMUserException: {err}".format(err=edue))
            return None
        except Errors.EDAMNotFoundException, ednfe:
            ## Parent Notebook GUID doesn't correspond to an actual notebook
            self.logger.error("EDAMNotFoundException: Invalid parent notebook GUID")
            return None
        ## Return created note object
        return note


    #---------------------------------------------------------------------------
    # Get evernote data
    #---------------------------------------------------------------------------
    def sync_data(self, gardening_notes, force_sync):
        '''
        Function gets evernote data and updates gardening JSON file

        key
        gardening_notes Dictionary with results from file
        cfg             Configuration set up
                            "gardening_tag":    Evernote gardening tag parent
                            "notebook":         Evernote notebook
                            "plant_tag_id":     Evernote plant tag parent
                            "location_tag_id":  Evernote location tag parent
                            "state_tag_id":     Evernote plant state tag parent
                            "sand_box":         Use Evernote sandbox account
                            "force_sync":       Force sync

        '''

        #---------------------------------------------------------------------------
        # GET EVERNOTE DATA AND WRITE TO FILE
        #---------------------------------------------------------------------------
        try:

            self.cfg['force_sync'] = force_sync

            user        = self.user_store.getUser()
            user_public = self.user_store.getPublicUserInfo(user.username)


            #------------------------------------------------------------------------
            # Check sync state
            #------------------------------------------------------------------------
            state = self.note_store.getSyncState()

            afterUSN = gardening_notes['lastUpdateCount']

            if self.cfg['force_sync']:
                afterUSN = 0

            if state.updateCount <= afterUSN:
                self.logger.info('Local file is in sync with Evernote. Exiting...')
                sys.exit()

            if afterUSN > 0:
                self.logger.info('Sync: INCREMENTAL')
            else:
                self.logger.info('Sync: FULL')


            #------------------------------------------------------------------------
            # Find notebook
            #------------------------------------------------------------------------
            notebooks       = self.note_store.listNotebooks()
            notebook_tag    = get_guid(notebooks, self.cfg['notebook']).keys()[0]


            #------------------------------------------------------------------------
            # Get all tags
            #------------------------------------------------------------------------
            tags            = self.note_store.listTags()

            gardening_notes['plant_tags']   = get_guid(tags, self.cfg['plant_tag_id'])
            gardening_tag                   = get_guid(tags, self.cfg['gardening_tag']).keys()[0]
            gardening_loc_tag               = get_guid(tags, self.cfg['location_tag_id']).keys()
            gardening_state_tag             = get_guid(tags, self.cfg['state_tag_id']).keys()     
            p_number_tag                    = get_guid(tags, self.cfg['plant_no_id']).keys()

            if len(gardening_state_tag) > 1 or len(gardening_loc_tag) > 1 or len(gardening_loc_tag) > 1:
                self.logger.error("More than one Tag Parent found. Exiting...")
                sys.exit()

            gardening_notes['location_tags']    = get_tag_children(tags, gardening_loc_tag[0])
            gardening_notes['state_tags']       = get_tag_children(tags, gardening_state_tag[0])
            gardening_notes['p_number_tags']    = get_tag_children(tags, p_number_tag[0])


            #------------------------------------------------------------------------
            # Get all notes with specific tag from notebook
            #------------------------------------------------------------------------
            filter = NoteStore.NoteFilter()
            filter.tagGuids = [gardening_tag]
            filter.notebookGuid = notebook_tag

            note_count = self.note_store.findNoteCounts(self.key['AUTH_TOKEN'], filter, False)
            note_count = note_count.notebookCounts[notebook_tag]

            if note_count <= 0:
                self.logger.error('No notes found. Exiting...')
                sys.exit()


            spec = NoteStore.SyncChunkFilter()
            spec.includeNotes = True
            spec.includeNoteResources = True
            spec.notebookGuids = [notebook_tag]

            self.logger.debug('Number of gardening notes found: {count}'.format(count=note_count))
            self.logger.debug('Downloading note metadata from evernote - START')

            note_list = []

            while True:
                self.logger.debug('USN {usn}/{count}'.format(usn=afterUSN, count=state.updateCount))
                download_data = self.note_store.getFilteredSyncChunk(
                    self.key['AUTH_TOKEN'],
                    afterUSN,
                    500,
                    spec)

                afterUSN = download_data.chunkHighUSN

                if download_data.notes:
                    note_list += download_data.notes
                    self.logger.debug('Number of notes downloaded {count}'.format(
                        count=len(download_data.notes)))

                if afterUSN >= state.updateCount or not afterUSN:
                    break


            self.logger.debug('Downloading note metadata from evernote - COMPLETE')


            #------------------------------------------------------------------------
            # Add new update count
            #------------------------------------------------------------------------
            gardening_notes['lastUpdateCount'] = download_data.updateCount



            #------------------------------------------------------------------------
            # Organize data and write to file
            #------------------------------------------------------------------------
            
            # Grab all plant and location tags
            all_plant_tags = gardening_notes['plant_tags'].keys()
            all_loc_tags = gardening_notes['location_tags'].keys()

            # Loop through all notes
            for note in note_list:

                # Check if note has been deleted
                if note.deleted:
                    if note.guid in gardening_notes['notes']:
                        del gardening_notes['notes'][note.guid]
                        self.logger.info('Deleted note: {guid} - {title}'.format(
                            guid=note.guid,
                            title=note.title))
                    continue

                # Ignore note if updated prior to current sequence number
                if note.guid in gardening_notes['notes']:
                    if note.updateSequenceNum < gardening_notes['notes'][note.guid]['USN']:
                        continue

                # Ignore if note not in designated notebook
                if notebook_tag not in note.notebookGuid:
                    continue

                # Ignore if gardening tag is not present
                if gardening_tag not in note.tagGuids:
                    continue

                # Populate list of plant and location tags in note
                plant_tags = []
                loc_tags = []
                for tag in note.tagGuids:
                    if tag in all_plant_tags:
                        plant_tags.append(tag)
                    elif tag in all_plant_tags:
                        loc_tags.append(tag)

                # Ignore if no plant or location tags
                if not plant_tags and not loc_tags:
                    continue

                # Grab image
                res_guid = []
                if note.resources:
                    for i in xrange(len(note.resources)):
                        if note.resources[i].mime == 'image/jpeg':
                            res_guid.append('{user}res/{r_guid}'.format(
                                user=user_public.webApiUrlPrefix,
                                r_guid=note.resources[i].guid))

                # Update list
                self.logger.info('Note updated: {guid} - {title}'.format(guid=note.guid, title=note.title))

                gardening_notes['notes'][note.guid] = {
                    'created':  note.created,
                    'title':    note.title,
                    'tags':     note.tagGuids,
                    'res':      res_guid,
                    'USN':      note.updateSequenceNum,
                    'link':     'https://{service}/shard/{shardId}/nl/{userId}/{noteGuid}/'.format(
                                        service=self.key['SERVICE'],
                                        shardId=user.shardId,
                                        userId=user.id,
                                        noteGuid=note.guid)
                }  
        
            self.logger.debug('Sorting data: COMPLETE')
            self.logger.debug('Notes stored: {stored_no} / {total_no}'.format(
                                    stored_no= len(gardening_notes['notes']),
                                    total_no= note_count))

            self.logger.info('Sync Complete')

            return gardening_notes


        #---------------------------------------------------------------------------
        # Error Handling
        #---------------------------------------------------------------------------
        except Errors.EDAMSystemException, e:
            if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
                self.logger.error("Rate limit reached")
                self.logger.error("Retry your request in %d seconds" % e.rateLimitDuration)
                
            if e.errorCode == Errors.EDAMErrorCode.INVALID_AUTH:
                self.logger.error("Invalid Authentication")

            sys.exit()

        except Exception, e:
            self.logger.error('Script error ({error_v}). Exiting...'.format(
                error_v=e), exc_info=True)
            # wd_err.set()
            sys.exit()


#---------------------------------------------------------------------------
# Get evernote data
#---------------------------------------------------------------------------
def get_config_data(key_file, cfg_file):
    '''
    Function gets evernote configuration data

    key             Key file location and name
    cfg             Configuration file location and name

    '''


    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = logging.getLogger('root')

    #---------------------------------------------------------------------------
    # GET EVERNOTE DATA AND WRITE TO FILE
    #---------------------------------------------------------------------------
    try:
        with open(cfg_file, 'r') as f:
            config = json.load(f)

        with open(key_file, 'r') as f:
            key = json.load(f)

        return config, key
   
    except Exception, e:
        logger.error('Error ({error_v}). Exiting...'.format(error_v=e), exc_info=True)
        # wd_err.set()
        sys.exit()

#---------------------------------------------------------------------------
# Displays help
#---------------------------------------------------------------------------
def usage():
    print('en_tools.py')


#---------------------------------------------------------------------------
# Nested dictionaries
#---------------------------------------------------------------------------
def nested_dict():
    return collections.defaultdict(nested_dict)


#---------------------------------------------------------------------------
# Nested dictionaries
#---------------------------------------------------------------------------
def prepare_dates(time_since_epoch):
    date = datetime.datetime.fromtimestamp(time_since_epoch)
    year = int(date.strftime('%Y'))
    month = date.strftime('%m')
    week = date.isocalendar()[1]

    # If week 53 and month is January then it should be the previous year line
    if week > 4 and month == '01':
        year -= 1

    return week, month, year


#---------------------------------------------------------------------------
# Sort gardening data for web page
#---------------------------------------------------------------------------
def web_format(data, state_data):
    '''
    Formats data into a usable json for the web page
    '''


    # Set up logger
    logger = logging.getLogger('root')


    routine_start = datetime.datetime.now();

    plants = data['plant_tags']
    states = data['state_tags']
    locations = data['location_tags']
    plant_no = data['p_number_tags']

    d = nested_dict()

    for note_id in data['notes']:
        note = data['notes'][note_id]

        # Prepare dates
        week, month, year = prepare_dates(note['created']/1000)

        # Get note information
        image_link = note['res'][0] if note['res'] else ''
        
        note_plants_no =    [float(plant_no[tag].replace('+p', '')) for tag in note['tags'] if tag in plant_no]
        note_states =       [tag for tag in note['tags'] if tag in states]
        note_symbols =      [state_data[tag]['symbol'] for tag in note['tags'] if tag in states]
        note_color =        [state_data[tag]['color'] for tag in note['tags'] if tag in states if state_data[tag]['color']]
        note_locations =    [tag for tag in note['tags'] if tag in locations]

        # Move to next note if no state tagged 
        if not note_states:
            continue
        
        if not note_plants_no:
            note_plants_no = [float('01.00')]

        note_event = [state_data[state]['event'] for state in note_states if state_data[state]['event'] is not 'single']

        # These are ordered in priority of event 
        if 'division' in note_event or 'merge' in note_event:
            for symbol in note_symbols:
                if type(symbol) is dict:
                    parent = symbol['parent']
                    child = symbol['child']
                    note_symbols.remove(symbol)
                    break
            note_event = 'merge' if 'merge' in note_event else 'division'
        elif 'dead' in note_event:      
            note_event_display = 'dead'
        elif 'start' in note_event:      
            note_event_display = 'start'
        elif 'end' in note_event:      
            note_event_display = 'end'
        elif 'continous' in note_event:      
            note_event_display = 'continous'
        else:
            note_event_display = ''

        # Create a timeline for each plant tagged in a note
        for tag in note['tags']:
            if tag in plants:

                for p in note_plants_no:

                    # Add symbol for states with multiple symbols
                    if note_event is 'division' or note_event is 'merge':
                        if p is min(note_plants_no):
                            note_symbols = [parent]
                        else:
                            note_symbols = [child]
                            note_event_display = 'dead' if note_event is 'merge' else 'start'

                    # Create new record if not present
                    if year not in d[tag][p]['timeline'].keys():
                        d[tag][p]['timeline'][year] = [None]*53
                    
                    # Replace " as it causes issues with the html later
                    title = note['title'].replace('\"', "'")
                    
                    #Add note data to week
                    if not d[tag][p]['timeline'][year][week-1]:
                        d[tag][p]['timeline'][year][week-1] = {
                            'title':        title,
                            'body':         [[title, note['link']]],
                            'states':       note_states,
                            'locations':    note_locations,
                            'color':        note_color,
                            'event':        note_event_display,    
                            'symbols':      note_symbols,
                            'image':        image_link
                        }
                    else:
                        # Add new note items
                        # but remove duplicate items by using sets
                        week_d = d[tag][p]['timeline'][year][week-1]
                        week_d['title']     = 'Multiple Notes'
                        week_d['body'].append([title, note['link']])
                        week_d['states']    = list(set(week_d['states'])|set(note_states))
                        week_d['locations'] = list(set(week_d['locations'])|set(note_locations))
                        week_d['symbols']   = list(set(week_d['symbols'])|set(note_symbols))
                        week_d['color']     = list(set(week_d['color'])|set(note_color))
                        if note_event_display and week_d['event'] not in ['start', 'dead', 'end']:
                            week_d['event'] = note_event_display
                        if not week_d['image']:
                            week_d['image'] = image_link

    f = nested_dict()
    for plant in d:
        for n in d[plant]:
            events = [d[plant][n]['timeline'][y][w]['event'] for y in d[plant][n]['timeline'] for w in range(53) if d[plant][n]['timeline'][y][w]]
            if 'start' in events:
                f[plant][n] = d[plant][n]

    routine_end = datetime.datetime.now()

    logger.debug('Time taken {duration}'.format(duration= routine_end-routine_start))


    return f


#---------------------------------------------------------------------------
# Grabs weekly weather data from previous 3 years and compiles it into a dictionary
#---------------------------------------------------------------------------
def weekly_weather(folder_loc):
    
    year_current = datetime.datetime.now().year

    weekly_data = nested_dict()

    # Grab data from csv files    
    for year in range(year_current, year_current - 2, -1):
        print year
        try:
            with open('{fl}/data/weekly_summary_{year}.csv'.format(fl= folder_loc, year= year), 'rb') as f:
                reader = csv.reader(f)
                data = list(reader)

            # Remove header
            data[0] = None

            # Grab data
            for row in data:
                if row:
                    # Prepare dates
                    week, month, year = prepare_dates(int(row[0]))

                    weekly_data[week][year] = {
                        'Outside_MIN':  row[1],
                        'Outside_AVG':  row[2],
                        'Precip_TOTAL': row[3]
                    }
        
        except IOError:
            continue

    # Calculate weekly averages
    for w in range(1,54):
        years = weekly_data[w].keys()

        for item in ['Outside_MIN', 'Outside_AVG', 'Precip_TOTAL']:
            try:
                weekly_data[w]['AVG'][item] = sum(float(weekly_data[w][y][item]) for y in years) / len(years)
            except Exception, e:
                weekly_data[w]['AVG'][item] = None
        
    return weekly_data


#===============================================================================
# MAIN
#===============================================================================
def main():

    '''
    Syncronizes data from evernote locally

    Passed arguments:

        -b, --sandbox           - Use sandbox account
        -s, --force-sync        - Force complete sync with evernote. Replaces all
                                  existing data. Allows no other commands to run
                                  except --sandbox.
        -x, --sync-off          - Run script wihout partial syncing to evernote 
                                  account. 
        -c, --created=""        - Date for note to be created. Format 2017-12-31 
                                  or in week number 2017-W38 which will pick the 
                                  Thursday date in that week
    '''
   
    script_name = os.path.basename(sys.argv[0])
    folder_loc  = os.path.dirname(os.path.realpath(sys.argv[0]))
    folder_loc  = folder_loc.replace('scripts', '')


    #---------------------------------------------------------------------------
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = log.setup('root', '{folder}/logs/{script}.log'.format(
                                                    folder= folder_loc,
                                                    script= script_name[:-3]))
    logger.info('')
    logger.info('--- Script {script} Started ---'.format(script= script_name))


    #---------------------------------------------------------------------------
    # SET UP WATCHDOG
    #---------------------------------------------------------------------------
    err_file    = '{fl}/data/error.json'.format(fl= folder_loc)
    # wd_err      = wd.ErrorCode(err_file, '0007')


    #---------------------------------------------------------------------------
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------  
    if check_process.is_running(script_name):
        # wd_err.set()
        sys.exit()


    #---------------------------------------------------------------------------
    # CHECK USER REQUESTS
    #---------------------------------------------------------------------------    
    try:

        key_file = 'evernote_key.json'
        sand_box = False
        sync = True
        force_sync = False
        new_note = False
        format_into_web = False
        file_csv = False
        note_data = {
                'created':  int(datetime.datetime.now().strftime("%s")) * 1000,
                'title':    'new note',
                'body':     '',
                'tags':     [],
                'notebook': None
            }
 
        try:
            opts, args = getopt.getopt(sys.argv[1:],'hxf:wst:g:c:',
                ['help', 'sync-off', 'csv=', 'web', 'force-sync', 'sandbox', 'title=', 'tags=', 'created='])
        except getopt.GetoptError:
            usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-b', '--sandbox'):
                key_file = 'evernote_key_sand.json'
                logger.info('Using Evernote sandbox')
                sand_box = True 
                continue

            if opt in ('-s', '--force-sync'):
                logger.info('Force sync requested')
                force_sync = True
                break

            if opt in ('-x', '--sync-off'):
                logger.info('No sync requested')
                sync = False
                continue

            if opt in ('-w', '--web'):
                format_into_web = True
                continue

            if opt in ('-h', '--help'):
                usage()
                sys.exit()

            if opt in ('-f', '--csv'):
                csv_file_name = arg
                sync = False
                new_note = True
                file_csv = True
                break

            if opt in ('-t', '--title'):
                note_data['title'] = arg
                sync = False
                new_note = True
                continue

            if opt in ("-g", "--tags"):
                note_data['tags'] = arg.split(',')
                continue

            if opt in ("-c", "--created"):
                note_data['created'] = arg
                continue

        config, key =   get_config_data(cfg_file= '{fl}data/config.json'.format(fl= folder_loc), 
                                        key_file= '{fl}keys/{fk}'.format(fl= folder_loc, 
                                                                         fk=key_file))

        EnAcc = EvernoteAcc(key, config, sand_box)


        #---------------------------------------------------------------------------
        # WRITE ENTRY OTHERWISE UPDATE DATA FILE
        #---------------------------------------------------------------------------
        if new_note:
            if file_csv:
                with open('{fl}data/{file}'.format(fl= folder_loc, file= csv_file_name), 'rb') as f:
                    reader = csv.reader(f)
                    data = list(reader)
                records = []
                for row in data:
                    if row:
                        new_data = note_data.copy()
                        new_data['created'] = row[0]
                        new_data['title'] = row[1]
                        new_data['tags'] = [row[tag] for tag in range(2,len(row))]
                        records.append(new_data)
            else:
                records = [note_data]

            for item in records:

                # Sort out dates
                if 'W' in item['created']:
                    date = get_thrs_date_from_iso_week(item['created'])
                else:
                    date = datetime.datetime.strptime(item['created'], '%Y-%m-%d')
                item['created'] = int(date.strftime("%s")) * 1000

                logger.info('New note date: {d}'.format(d=item['created']))
                logger.info('New note title: {t}'.format(t=item['title']))
                logger.info('New note tags: {t}'.format(t=item['tags']))

                note = EnAcc.new_entry(item)

            sys.exit()




        #---------------------------------------------------------------------------
        # READ DATA FROM EN AND WRITE TO FILE
        #---------------------------------------------------------------------------
        try:
            with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'r') as f:
                gardening_notes = json.load(f)

        except Exception, e:
            if format_into_web and not sync:
                logger.error('Error ({error_v}). Exiting...'.format(error_v=e), exc_info=True)
                sys.exit()

            if sync:
                logger.warning('Warning ({error_v}).'.format(error_v=e), exc_info=True)
                gardening_notes = {
                        'lastUpdateCount': 0, 
                        'plant_tags': {}, 
                        'state_tags': {},
                        'location_tags': {}, 
                        'p_number_tags': {}, 
                        'notes': {}
                    }

        if sync:
            logger.info('Synchronizing with evernote.')

            gardening_notes = EnAcc.sync_data(gardening_notes, force_sync)

            with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'w') as f:
                json.dump(gardening_notes, f)

            logger.debug('Writting data to file: COMPLETE')

            state_config = check_state_tags(gardening_notes['state_tags'], '{fl}/data/state_tags.json'.format(fl= folder_loc))
            

        if format_into_web:
            logger.info('Organize garden data into web format')

            if not sync:
                with open('{fl}/data/state_tags.json'.format(fl= folder_loc), 'r') as f:
                    state_config = json.load(f)

            formatted_gardening_notes = {}
            formatted_gardening_notes['diary'] = web_format(gardening_notes, state_config)
            formatted_gardening_notes['plant_tags'] = gardening_notes['plant_tags']
            formatted_gardening_notes['location_tags'] = gardening_notes['location_tags']
            formatted_gardening_notes['weekly_weather'] = weekly_weather(folder_loc)


            with open('{fl}/data/gardening_web.json'.format(fl= folder_loc), 'w') as f:
                json.dump(formatted_gardening_notes, f)


    except Exception, e:
        logger.error('Error ({error_v}). Exiting...'.format(error_v=e), exc_info=True)
        # wd_err.set()
        sys.exit()


    finally:
        logger.info('--- Script Finished ---')


#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()

