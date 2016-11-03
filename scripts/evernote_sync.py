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




#---------------------------------------------------------------------------
# Get evernote data
#---------------------------------------------------------------------------
def get_evernote_data(key, gardening_notes, cfg):
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
    # SET UP LOGGER
    #---------------------------------------------------------------------------
    logger = logging.getLogger('root')

    #---------------------------------------------------------------------------
    # GET EVERNOTE DATA AND WRITE TO FILE
    #---------------------------------------------------------------------------
    try:

        client = EvernoteClient(token=key['AUTH_TOKEN'], sandbox=cfg['sand_box'])
        
        note_store  = client.get_note_store()
        user_store  = client.get_user_store()
        user        = user_store.getUser()
        user_public = user_store.getPublicUserInfo(user.username)

        #------------------------------------------------------------------------
        # Check evernote API
        #------------------------------------------------------------------------
        version_ok = user_store.checkVersion(
            "Evernote EDAMTest (Python)",
            UserStoreConstants.EDAM_VERSION_MAJOR,
            UserStoreConstants.EDAM_VERSION_MINOR)

        if not version_ok:
            logger.warning("Evernote API version is not up to date.")


        #------------------------------------------------------------------------
        # Check sync state
        #------------------------------------------------------------------------
        state = note_store.getSyncState()

        afterUSN = gardening_notes['lastUpdateCount']

        if cfg['force_sync']:
            afterUSN = 0

        if state.updateCount <= afterUSN:
            logger.info('Local file is in sync with Evernote. Exiting...')
            sys.exit()

        if afterUSN > 0:
            logger.info('Sync: INCREMENTAL')
        else:
            logger.info('Sync: FULL')


        #------------------------------------------------------------------------
        # Find notebook
        #------------------------------------------------------------------------
        notebooks       = note_store.listNotebooks()
        notebook_tag    = get_guid(notebooks, cfg['notebook']).keys()[0]


        #------------------------------------------------------------------------
        # Get all tags
        #------------------------------------------------------------------------
        tags            = note_store.listTags()

        gardening_notes['plant_tags']   = get_guid(tags, cfg['plant_tag_id'])
        gardening_tag                   = get_guid(tags, cfg['gardening_tag']).keys()[0]
        gardening_loc_tag               = get_guid(tags, cfg['location_tag_id']).keys()
        gardening_state_tag             = get_guid(tags, cfg['state_tag_id']).keys()     
        p_number_tag                    = get_guid(tags, cfg['plant_no_id']).keys()

        if len(gardening_state_tag) > 1 or len(gardening_loc_tag) > 1 or len(gardening_loc_tag) > 1:
            logger.error("More than one Tag Parent found. Exiting...")
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

        note_count = note_store.findNoteCounts(key['AUTH_TOKEN'], filter, False)
        note_count = note_count.notebookCounts[notebook_tag]

        if note_count <= 0:
            logger.error('No notes found. Exiting...')
            sys.exit()


        spec = NoteStore.SyncChunkFilter() 
        spec.includeNotes = True
        spec.includeNoteResources = True
        spec.notebookGuids = [notebook_tag]

        logger.debug('Number of gardening notes found: {count}'.format(count= note_count))
        logger.debug('Downloading note metadata from evernote - START')

        note_list = []

        while True:
            logger.debug('USN {usn} / {count}'.format(usn= afterUSN, count= state.updateCount))
            download_data = note_store.getFilteredSyncChunk(key['AUTH_TOKEN'], afterUSN, 500, spec)

            afterUSN = download_data.chunkHighUSN

            if download_data.notes:
                note_list += download_data.notes
                logger.debug('Number of notes downloaded {count}'.format(count= len(download_data.notes)))
            
            if afterUSN >= state.updateCount or not afterUSN:
                break

    
        logger.debug('Downloading note metadata from evernote - COMPLETE')


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

            logger.info('Note updated: {guid} - {title}'.format(guid= note.guid, title=note.title))

            gardening_notes['notes'][note.guid] = {
                'created':  note.created,
                'title':    note.title,
                'tags':     note.tagGuids,
                'res':      res_guid,
                'USN':      note.updateSequenceNum,
                'link':     'https://{service}/shard/{shardId}/nl/{userId}/{noteGuid}/'.format(
                                    service= key['SERVICE'],
                                    shardId= user.shardId,
                                    userId= user.id,
                                    noteGuid= note.guid)
            }  
    
        logger.debug('Sorting data: COMPLETE')
        logger.debug('Notes stored: {stored_no} / {total_no}'.format(
                                stored_no= len(gardening_notes['notes']),
                                total_no= note_count))

        logger.info('Sync Complete')

        return gardening_notes


    #---------------------------------------------------------------------------
    # Error Handling
    #---------------------------------------------------------------------------
    except Errors.EDAMSystemException, e:
        if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
            logger.error("Rate limit reached")
            logger.error("Retry your request in %d seconds" % e.rateLimitDuration)
            
        if e.errorCode == Errors.EDAMErrorCode.INVALID_AUTH:
            logger.error("Invalid Authentication")


        sys.exit()

    except Exception, e:
        logger.error('Script error ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        # wd_err.set()
        sys.exit()



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
    key_file = 'evernote_key.json'
    sand_box = False
    force_sync = False

    if len(sys.argv) > 1:
        if '-s' in sys.argv:
            key_file = 'evernote_key_sand.json'
            sand_box = True 
        if '-f' in sys.argv:
            force_sync = True 


    #---------------------------------------------------------------------------
    # GET CONFIG & GARDENING DATA
    #---------------------------------------------------------------------------
    try:
        with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'r') as f:
            gardening_notes = json.load(f)

    except Exception, e:
        logger.warning('Warning ({error_v}).'.format(error_v=e), exc_info=True)

        gardening_notes = {
            'lastUpdateCount': 0, 
            'plant_tags': {}, 
            'state_tags': {},
            'location_tags': {}, 
            'p_number_tags': {}, 
            'notes': {}
        }

    try:
        with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
            config = json.load(f)

        with open('{fl}keys/{fk}'.format(fl= folder_loc, fk=key_file), 'r') as f:
            key = json.load(f)


        cfg = { 
            "gardening_tag":    config['evernote']['GARDENING_TAG'],
            "notebook":         config['evernote']['NOTEBOOK'],
            "plant_tag_id":     config['evernote']['PLANT_TAG_ID'],
            "location_tag_id":  config['evernote']['LOCATION_TAG_ID'],
            "state_tag_id":     config['evernote']['STATE_TAG_ID'],
            "plant_no_id":      '+plants', #config['evernote']['PLANT_NO_TAG_ID'],
            "sand_box":         sand_box, 
            "force_sync":       force_sync
        }


        gardening_notes = get_evernote_data(key, gardening_notes, cfg)

        with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'w') as f:
            json.dump(gardening_notes, f)

        logger.debug('Writting data to file: COMPLETE')

        check_state_tags(gardening_notes['state_tags'], '{fl}/data/state_tags.json'.format(fl= folder_loc))
   
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

