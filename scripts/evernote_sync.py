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
    # with open('{fl}/data/config.json'.format(fl= folder_loc), 'r') as f:
    #     config = json.load(f)

    gardening_tag_name = '!gardening'

    with open(self.file_loc, 'r') as f:
            return json.load(f)




    #---------------------------------------------------------------------------
    # GET EVERNOTE DATA
    #---------------------------------------------------------------------------
    authToken = "S=s1:U=92f9a:E=15ee8b5fe6c:C=1579104cf10:P=1cd:A=en-devtoken:V=2:H=f5a3445b1ba2c095195f3491ef21d797"

    client = EvernoteClient(token=authToken, sandbox=True)
    
    user_store = client.get_user_store()

    version_ok = user_store.checkVersion(
        "Evernote EDAMTest (Python)",
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR
    )

    logger.info("Is my Evernote API version up to date? {response}".format(response= str(version_ok)))
    if not version_ok:
        exit(1)

    note_store = client.get_note_store()

    state = note_store.getSyncState()
    logger.info(state)


    tags = note_store.listTags()

    # for tag in tags:
    #     logger.info(tag)

    # Search for a tag
    gardening_tag = [tag.guid for tag in tags if tag.name == gardening_tag_name]  
    logger.info(gardening_tag)

    filter = NoteStore.NoteFilter()
    filter.tagGuids = gardening_tag

    spec = NoteStore.NotesMetadataResultSpec()
    spec.includeTitle = True
    spec.includeCreated = True
    spec.includeTagGuids = True

    ourNoteList = note_store.findNotesMetadata(authToken, filter, 0, 10000, spec)

    for notes in ourNoteList.notes:
        logger.info(notes)


    #---------------------------------------------------------------------------
    # WRITE EVERNOTE DATA TO JSON
    #---------------------------------------------------------------------------
    # with open('{fl}/data/gardening.json'.format(fl= folder_loc), 'w') as f:
    #     json.dump(data, f)


#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()

