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
from evernote.api.client import EvernoteClient

# Application modules
import settings as s
import log
import check_process
# import watchdog as wd


#---------------------------------------------------------------------------
# Get guid for tag
#---------------------------------------------------------------------------
def get_tag_guid(tag_list, search_string):
    '''
    Function returns the tag guid from a list

    tag_list        Struct: Tag as defined by Evernote
    search_string   string of tag name to search 

    '''

    return {tag.guid: tag.name for tag in tag_list if tag.name.find(search_string) > -1}


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
    # GET CONFIG & GARDENING DATA
    #---------------------------------------------------------------------------
    try:
        with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
            config = json.load(f)
        with open('{fl}/data/key.json'.format(fl= folder_loc), 'r') as f:
            key = json.load(f)
    except Exception, e:
        logger.error('Error ({error_v}). Exiting...'.format(error_v=e), exc_info=True)
        # wd_err.set()
        sys.exit()

    try:
        with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'r') as f:
            gardening_notes = json.load(f)
    except Exception, e:
        logger.warning('Error ({error_v}).'.format(error_v=e), exc_info=True)



    #---------------------------------------------------------------------------
    # GET EVERNOTE DATA AND WRITE TO FILE
    #---------------------------------------------------------------------------
    try:

        client = EvernoteClient(token=key['AUTH_TOKEN'], sandbox=True)
        
        note_store = client.get_note_store()
        user_store = client.get_user_store()
        user = user_store.getUser()


        # Check evernote API
        version_ok = user_store.checkVersion(
            "Evernote EDAMTest (Python)",
            UserStoreConstants.EDAM_VERSION_MAJOR,
            UserStoreConstants.EDAM_VERSION_MINOR)

        if not version_ok:
            logger.warning("Evernote API version is not up to date.")


        # Check sync state
        state = note_store.getSyncState()
        if state.updateCount <= gardening_notes['sync_updateCount']:
            logger.info('Local file is in sync with Evernote. Exiting...')
            # sys.exit()

        logger.info('Syncing local data with Evernote...')


        # Reset data
        gardening_notes = {
            'sync_updateCount': 0, 
            'plant_tags': {}, 
            'state_tags': {},
            'location_tags': {}, 
            'notes': {}
        }


        # Add new update count
        gardening_notes['sync_updateCount'] = state.updateCount


        # Get all tags and search for a specific tag
        tags            = note_store.listTags()
        gardening_tag   = get_tag_guid(tags, config['evernote']['GARDENING_TAG'])
        gardening_notes['plant_tags']  = get_tag_guid(tags, config['evernote']['PLANT_TAG_ID'])
      
        gardening_loc_tag = get_tag_guid(tags, config['evernote']['LOCATION_TAG_ID']).keys()

        if len(gardening_loc_tag) > 1:
            logger.error("More than one Location Tag Parent found. Exiting...")
            sys.exit()

        gardening_notes['location_tags']  = get_tag_children(tags, gardening_loc_tag[0])

        gardening_state_tag = get_tag_guid(tags, config['evernote']['STATE_TAG_ID']).keys()

        if len(gardening_state_tag) > 1:
            logger.error("More than one State Tag Parent found. Exiting...")
            sys.exit()

        gardening_notes['state_tags']  = get_tag_children(tags, gardening_state_tag[0])




        # Get all notes with specific tag
        filter = NoteStore.NoteFilter()
        filter.tagGuids = gardening_tag.keys()

        spec = NoteStore.NotesMetadataResultSpec()
        spec.includeTitle = True
        spec.includeCreated = True
        spec.includeTagGuids = True

        note_list = note_store.findNotesMetadata(key['AUTH_TOKEN'], filter, 0, 10000, spec)

        for note in note_list.notes:
            gardening_notes['notes'][note.guid] = {
                'created':  note.created,
                'title':    note.title,
                'tags':     note.tagGuids,
                'link':     'https://{service}/shard/{shardId}/nl/{userId}/{noteGuid}/'.format(
                                    service= key['SERVICE'],
                                    shardId= user.shardId,
                                    userId= user.id,
                                    noteGuid= note.guid)
            }


        # Write gardening data to 
        with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'w') as f:
            json.dump(gardening_notes, f)


        logger.info('Sync Complete')


    except Exception, e:
        logger.error('Script error ({error_v}). Exiting...'.format(
            error_v=e), exc_info=True)
        # wd_err.set()
        sys.exit()

    finally:
        logger.info('--- Script Finished ---')


#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()

