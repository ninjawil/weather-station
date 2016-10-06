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


#---------------------------------------------------------------------------
# Get guid for tag
#---------------------------------------------------------------------------
def get_tag_guid(tag_list, search_string):
    '''
    Function returns the tag guid from a list

    tag_list        Struct: Tag as defined by Evernote
    search_string   string of tag name to search 

    '''

    return {tag.name: tag.guid for tag in tag_list if tag.name.find(search_string) > -1}



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
    # CHECK SCRIPT IS NOT ALREADY RUNNING
    #---------------------------------------------------------------------------    
    if check_process.is_running(script_name):
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
        sys.exit()

    try:
        with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'r') as f:
            gardening_notes = json.load(f)
    except Exception, e:
        logger.warning('Error ({error_v}).'.format(error_v=e), exc_info=True)
        gardening_notes = {'sync_updateCount': 0, 'tags': {}, 'notes': {}}




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

        gardening_notes['sync_updateCount'] = state.updateCount

        logger.info('Syncing local data with Evernote...')


        # Get all tags and search for a specific tag
        tags            = note_store.listTags()
        gardening_tag   = get_tag_guid(tags, config['evernote']['GARDENING_TAG'])
        gardening_notes['tags']  = get_tag_guid(tags, config['evernote']['PLANT_TAG_ID'])


        # Get all notes with specific tag
        filter = NoteStore.NoteFilter()
        filter.tagGuids = [gardening_tag[config['evernote']['GARDENING_TAG']]]

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
        sys.exit()

    finally:
        logger.info('--- Script Finished ---')


#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()

