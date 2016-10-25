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
    key_file = 'key.json'
    sand_box = False
    force_sync = False
    force_sync = False

    if len(sys.argv) > 1:
        if '-s' in sys.argv:
            key_file = 'key_sand.json'
            sand_box = True 
        if '-f' in sys.argv:
            force_sync = True 


    #---------------------------------------------------------------------------
    # GET CONFIG & GARDENING DATA
    #---------------------------------------------------------------------------
    try:
        with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
            config = json.load(f)
        with open('{fl}/data/{fk}'.format(fl= folder_loc, fk=key_file), 'r') as f:
            key = json.load(f)
    except Exception, e:
        logger.error('Error ({error_v}). Exiting...'.format(error_v=e), exc_info=True)
        # wd_err.set()
        sys.exit()

    try:
        with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'r') as f:
            gardening_notes = json.load(f)

        afterUSN = gardening_notes['lastUpdateCount']

    except Exception, e:
        logger.warning('Error ({error_v}).'.format(error_v=e), exc_info=True)

        afterUSN = 0

        gardening_notes = {
            'lastUpdateCount': 0, 
            'plant_tags': {}, 
            'state_tags': {},
            'location_tags': {}, 
            'notes': {}
        }




    #---------------------------------------------------------------------------
    # GET EVERNOTE DATA AND WRITE TO FILE
    #---------------------------------------------------------------------------
    try:

        client = EvernoteClient(token=key['AUTH_TOKEN'], sandbox=sand_box)
        
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

        if force_sync:
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
        notebook_tag    = get_guid(notebooks, config['evernote']['NOTEBOOK']).keys()[0]


        #------------------------------------------------------------------------
        # Get all plant and location tags
        #------------------------------------------------------------------------
        tags            = note_store.listTags()
        gardening_tag   = get_guid(tags, config['evernote']['GARDENING_TAG']).keys()[0]

        gardening_notes['plant_tags']  = get_guid(tags, config['evernote']['PLANT_TAG_ID'])
      
        gardening_loc_tag = get_guid(tags, config['evernote']['LOCATION_TAG_ID']).keys()

        if len(gardening_loc_tag) > 1:
            logger.error("More than one Location Tag Parent found. Exiting...")
            sys.exit()

        gardening_notes['location_tags']  = get_tag_children(tags, gardening_loc_tag[0])

        gardening_state_tag = get_guid(tags, config['evernote']['STATE_TAG_ID']).keys()

        if len(gardening_state_tag) > 1:
            logger.error("More than one State Tag Parent found. Exiting...")
            sys.exit()

        gardening_notes['state_tags']  = get_tag_children(tags, gardening_state_tag[0])


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
        spec.notebookGuids = [notebook_tag]

        logger.debug('Number of notes to download: {count}'.format(count= note_count))
        logger.debug('Downloading note metadata from evernote - START')

        note_list = []

        # while True:
        logger.debug('USN {usn} / {count}'.format(usn= afterUSN, count= state.updateCount))
        download_data = note_store.getFilteredSyncChunk(key['AUTH_TOKEN'], afterUSN, 500, spec)

        afterUSN = download_data.chunkHighUSN

        note_list += download_data.notes
            
            # if afterUSN >= state.updateCount or not afterUSN:
            #     break

        logger.debug('Number of notes downloaded {count}'.format(count= len(download_data.notes)))
        
        logger.debug('Downloading note metadata from evernote - COMPLETE')


        #------------------------------------------------------------------------
        # Add new update count
        #------------------------------------------------------------------------
        gardening_notes['lastUpdateCount'] = download_data.updateCount

        note_list = [note for note in note_list if note.tagGuids in gardening_notes['plant_tags'].keys()]


        #------------------------------------------------------------------------
        # Organize data and write to file
        #------------------------------------------------------------------------
        for note in note_list:

            if gardening_tag in note.tagGuids and notebook_tag in note.notebookGuid:

                #if note.updateSequenceNum > gardening_notes['notes'][note.guid]['USN']:

                print note.title
                print note.resources
                print note.notebookGuid

                res_guid = []

                # if note.largestResourceMime == 'image/jpeg':
                #     logger.debug('Downloading note: {nt}'.format(nt=note.guid))
                #     note_detail = note_store.getNote(key['AUTH_TOKEN'], note.guid, False, False, False, False)

                #     for resource in note_detail.resources:
                #         res_guid.append('{user}res/{r_guid}'.format(user= user_public.webApiUrlPrefix, r_guid= resource.guid))


                gardening_notes['notes'][note.guid] = {
                    'created':  note.created,
                    'title':    note.title,
                    'tags':     note.tagGuids,
                    'res':      res_guid,
                    'USN':      note.updateSequenceNum
                    # 'link':     'https://{service}/shard/{shardId}/nl/{userId}/{noteGuid}/'.format(
                    #                     service= key['SERVICE'],
                    #                     shardId= user.shardId,
                    #                     userId= user.id,
                    #                     noteGuid= note.guid)
                }
    
        logger.debug('Sorting data: COMPLETE')


        with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'w') as f:
            json.dump(gardening_notes, f)
        logger.debug('Writting data to file: COMPLETE')


        logger.info('Sync Complete')


    #---------------------------------------------------------------------------
    # Exit and Error Handling
    #---------------------------------------------------------------------------
    except Errors.EDAMSystemException, e:
        if e.errorCode == Errors.EDAMErrorCode.RATE_LIMIT_REACHED:
            logger.error("Rate limit reached")
            logger.error("Retry your request in %d seconds" % e.rateLimitDuration)
            sys.exit()

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

