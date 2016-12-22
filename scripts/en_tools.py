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
                            "sand_box":         Use Evernote sandbox account, 
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
            filter.tagGuids     = [gardening_tag]
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

            self.logger.debug('Number of gardening notes found: {count}'.format(count= note_count))
            self.logger.debug('Downloading note metadata from evernote - START')

            note_list = []

            while True:
                self.logger.debug('USN {usn} / {count}'.format(usn= afterUSN, count= state.updateCount))
                download_data = self.note_store.getFilteredSyncChunk(self.key['AUTH_TOKEN'], afterUSN, 500, spec)

                afterUSN = download_data.chunkHighUSN

                if download_data.notes:
                    note_list += download_data.notes
                    self.logger.debug('Number of notes downloaded {count}'.format(count= len(download_data.notes)))
                
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
            for note in note_list:

                if note.deleted:
                    continue

                if notebook_tag not in note.notebookGuid:
                    continue

                if gardening_tag not in note.tagGuids:
                    continue

                all_plant_tags = gardening_notes['plant_tags'].keys()
                all_loc_tags = gardening_notes['location_tags'].keys()
                plant_tags = []
                loc_tags = []
                for tag in note.tagGuids:
                    if tag in all_plant_tags: 
                        plant_tags.append(tag)
                    elif tag in all_plant_tags: 
                        loc_tags.append(tag)

                if not plant_tags and not loc_tags:
                    continue

                if note.guid in gardening_notes['notes']:
                    if note.updateSequenceNum < gardening_notes['notes'][note.guid]['USN']:
                        continue

                res_guid = []
                if note.resources:
                    for i in xrange(len(note.resources)):
                        if note.resources[i].mime == 'image/jpeg':
                            res_guid.append('{user}res/{r_guid}'.format(
                                user= user_public.webApiUrlPrefix, 
                                r_guid= note.resources[i].guid))

                self.logger.info('Note updated: {guid} - {title}'.format(guid= note.guid, title=note.title))

                gardening_notes['notes'][note.guid] = {
                    'created':  note.created,
                    'title':    note.title,
                    'tags':     note.tagGuids,
                    'res':      res_guid,
                    'USN':      note.updateSequenceNum,
                    'link':     'https://{service}/shard/{shardId}/nl/{userId}/{noteGuid}/'.format(
                                        service= self.key['SERVICE'],
                                        shardId= user.shardId,
                                        userId= user.id,
                                        noteGuid= note.guid)
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
        date = datetime.datetime.fromtimestamp(note['created']/1000)
        year = date.strftime('%Y')
        week = date.isocalendar()[1]

        # Get note information
        image_link = note['res'][0] if note['res'] else ''
        
        note_plants_no =    [tag for tag in note['tags'] if tag in plant_no]
        note_states =       [tag for tag in note['tags'] if tag in states]
        note_symbols =      [state_data[tag]['symbol'] for tag in note['tags'] if tag in states]
        note_color =        [state_data[tag]['color'] for tag in note['tags'] if tag in states if state_data[tag]['color']]
        note_locations =    [tag for tag in note['tags'] if tag in locations]

        if not note_plants_no:
            note_plants_no = ['+p01.00']

        # Create a timeline for each plant tagged in a note
        for tag in note['tags']:
            if tag in plants:
                for p in note_plants_no:
                    if year not in d[tag][p].keys():
                        # Create new record if not present
                        d[tag][p][year] = [None]*53
                    
                    if not d[tag][p][year][week-1]:
                        #Add note data to week
                        d[tag][p][year][week-1] = {
                            'note_id':      [note_id],
                            'states':       note_states,
                            'locations':    note_locations,
                            'color':        note_color,
                            'symbols':      note_symbols,
                            'link':         note['link'],
                            'image':        image_link
                        }
                    else:
                        # Add new note items
                        # but remove duplicate items by using sets
                        week_d = d[tag][p][year][week-1]
                        week_d['note_id'].append(note_id)
                        week_d['states'] = list(set(week_d['states'])|set(note_states))
                        week_d['locations'] = list(set(week_d['locations'])|set(note_locations))
                        week_d['symbols'] = list(set(week_d['symbols'])|set(note_symbols))
                        week_d['color'] = list(set(week_d['color'])|set(note_color))

    routine_end = datetime.datetime.now()

    logger.debug('Time taken {duration}'.format(duration= routine_end-routine_start))

    #print d['644f1488-5a31-458a-b2e1-921a92243048'] # acer palmantum

    return d



#===============================================================================
# MAIN
#===============================================================================
def main():

    '''
    Syncronizes data from evernote locally
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
        sync = False
        force_sync = False
        new_note = False
        format_into_web = False
        note_data = {
                'created':  int(datetime.datetime.now().strftime("%s")) * 1000,
                'title':    'new note',
                'body':     '',
                'notebook': None
            }
 
        try:
            opts, args = getopt.getopt(sys.argv[1:],'hwfbt:c:',
                ['help', 'web', 'force-sync', 'sandbox', 'new', 'title=', 'created='])
        except getopt.GetoptError:
            usage()
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-b', '--sandbox'):
                key_file = 'evernote_key_sand.json'
                logger.info('Using Evernote sandbox')
                sand_box = True 
                continue

            if opt in ('-w', '--web'):
                logger.info('Organize garden data into web format')
                format_into_web = True
                break

            if opt in ('-f', '--force-sync'):
                logger.info('Force sync requested')
                force_sync = True
                break

            if opt in ('-h', '--help'):
                usage()
                sys.exit()

            if opt in ('-t', '--title'):
                note_data['title'] = arg
                sync = False
                new_note = True
                continue

            if opt in ("-c", "--created"):
                note_data['created'] = int(datetime.datetime.strptime(arg, '%Y-%m-%d').strftime("%s")) * 1000
                break

        config, key =   get_config_data(cfg_file= '{fl}/data/config.json'.format(fl= folder_loc), 
                                        key_file= '{fl}keys/{fk}'.format(fl= folder_loc, 
                                                                         fk=key_file))

        EnAcc = EvernoteAcc(key, config, sand_box)


        #---------------------------------------------------------------------------
        # WRITE ENTRY OTHERWISE UPDATE DATA FILE
        #---------------------------------------------------------------------------
        if new_note:
            note = EnAcc.new_entry(note_data)
            sys.exit()




        #---------------------------------------------------------------------------
        # READ DATA FROM EN AND WRITE TO FILE
        #---------------------------------------------------------------------------
        try:
            with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'r') as f:
                gardening_notes = json.load(f)

        except Exception, e:
            if format_into_web:
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
            gardening_notes = EnAcc.sync_data(gardening_notes, force_sync)

            with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'w') as f:
                json.dump(gardening_notes, f)

            logger.debug('Writting data to file: COMPLETE')

            state_config = check_state_tags(gardening_notes['state_tags'], '{fl}/data/state_tags.json'.format(fl= folder_loc))
            

        if format_into_web:

            if not sync:
                with open('{fl}/data/state_tags.json'.format(fl= folder_loc), 'r') as f:
                    state_config = json.load(f)

            formatted_gardening_notes = web_format(gardening_notes, state_config)

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

