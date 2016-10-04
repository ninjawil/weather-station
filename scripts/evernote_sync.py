#!usr/bin/env python

#===============================================================================
# Import modules
#===============================================================================
# Standard Library
import os
import sys
import datetime
import time

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

    # List all of the notebooks in the user's account
    notebooks = note_store.listNotebooks()
    logger.info("Found {no} notebooks:".format(no= len(notebooks)))
    for notebook in notebooks:
        logger.info( "  * {notebook} guid={guid}".format(notebook= notebook.name, guid= notebook.guid))

    tags = note_store.listTags()

    # for tag in tags:
    #     logger.info(tag)
    logger.info(tags)
    # logger.info(tags.name['!gardening'])


    filter = NoteStore.NoteFilter()
    filter.tagGuids = ['3c0cb026-a598-4495-9d4e-1c72c3d4f804']
    # filter.tagGuids = ['5ba98ad2-4fc5-489c-b0c9-0aa43d7e9bb9']

    noteCount = note_store.findNoteCounts(authToken, filter, False)
    logger.info(noteCount)




#===============================================================================
# Boiler plate
#===============================================================================
if __name__=='__main__':
    main()

