"""
Specification A functions and utilities for reading and validating databases.
"""

from ...spec import d 

import json
import os
import logging as log
from itertools import product

SPEC_A_JSON_FILENAME = "info.json"
KEY_TYPE = "type"
KEY_VERSION = "version"
VALUE_TYPE = "simple"
VALUE_VERSION = "1.1"
KEY_METADATA = "metadata"
KEY_METADATA_TYPE = "type"
VALUE_METADATA_TYPE = "parametric-image-stack"
KEY_NAME_PATTERN = "name_pattern"
KEY_ARGUMENTS = "arguments"
KEY_ARG_DEFAULT = "default"
KEY_ARG_LABEL = "label"
KEY_ARG_TYPE = "type"
KEY_ARG_VALUES = "values"

def get_dictionary(db_path, json_path=SPEC_A_JSON_FILENAME):
    """
    Get the dictionary for the json_path in the Cinema Spec A database.
    Does not validate that the database is a valid Spec A JSON file.
    If it is unable to open the JSON or parse it, it will return None.

    arguments:
        db_path : string
            POSIX path to Cinema database
        json_path : string = SPEC_A_JSON_FILENAME
            POSIX relative path to Cinema JSON 

    returns:
        a dictionary with the contents of a Spec A JSON or None
    """

    json_fn = os.path.join(db_path, json_path)
    if not os.path.exists(json_fn):
        return None
   
    try:
        with open(json_fn) as jf:
            return json.load(jf)
    except:
        return None

def get_iterator(db_path, json_path=SPEC_A_JSON_FILENAME):
    """
    Return a row iterator, assuming a valid Spec A database. Does
    not validate that it is a proper Spec A database. 

    This transforms the Spec A JSON into a row style (table style) iterator,
    which mirrors the Spec D iterator. That is the data are turned into
    columns and rows. The first row will be the "argument" to "column"
    mapping, i.e., the header identifiers will be argument names.

    Column order is determined by sorting the dimensions (parameters).

    arguments:
        db_path : string
            POSIX path to Cinema database
        json_path : string = SPEC_A_JSON_FILENAME
            POSIX relative path to Cinema JSON 

    returns:
        an iterator that returns a tuple of data per row if the json_path 
        file can be opened, otherwise returns None

        the first row will be the header (column identifiers), which are
        the arguments in the JSON file. The last column, will be FILE,
        i.e., the list of files.
    """
    db = get_dictionary(db_path, json_path)
    if db == None:
        return None

    try:
        keylist = tuple(sorted(db[KEY_ARGUMENTS].keys()))
        def filelist():
            yield keylist + (d.FILE_HEADER_KEYWORD,)
            for row in product(*[db[KEY_ARGUMENTS][k][KEY_ARG_VALUES] 
                                 for k in keylist]):
                kv = {k: v for k, v in zip(keylist, row)}
                yield row + (db[KEY_NAME_PATTERN].format(**kv),)
        return filelist()
    except:
        return None

def check_database(db_path, json_path=SPEC_A_JSON_FILENAME, quick=False):
    """
    Validate a Spec A database.

    arguments:
        db_path : string
            POSIX path to Cinema database
        json_path : string = SPEC_A_JSON_FILENAME
            POSIX relative path to Cinema JSON
        quick : boolean = False
            if True, perform a quick check, which means only checking
            validating the JSON, and not the files

    returns:
        True if it is valid, False otherwise

    side effects:
        logs error and info messages to the logger
    """

    log.info("Checking database \"{0}\" as Spec A.".format(db_path))

    try:
        log.info("Opening JSON file \"{0}\".".format(json_path))
        db = get_dictionary(db_path, json_path)
        if db == None:
            log.error("Error opening \"{0}\".".format(json_path))
            raise Exception("Error opening \"{0}\".".format(json_path))

        # check the unnecessary keys
        unnkey_error = False
        if KEY_TYPE not in db:
            log.warning("\"{0}\" not in JSON.".format(KEY_TYPE))
            unnkey_error = True
        elif db[KEY_TYPE] != VALUE_TYPE:
            log.warning("\"{0}\" is not \"{1}\".".format(KEY_TYPE, VALUE_TYPE))
            unnkey_error = True

        if KEY_VERSION not in db:
            log.warning("\"{0}\" not in JSON.".format(KEY_VERSION))
            unnkey_error = True
        elif db[KEY_VERSION] != VALUE_VERSION:
            log.warning("\"{0}\" is not \"{1}\".".format(KEY_VERSION, 
                VALUE_VERSION))
            unnkey_error = True

        if KEY_METADATA not in db:
            log.warning("\"{0}\" not in JSON.".format(KEY_METADATA))
            unnkey_error = True
        elif KEY_METADATA_TYPE not in db[KEY_METADATA]:
            log.warning("\"{0}\" not in \"{1}\".".format(KEY_METADATA_TYPE,
                KEY_METADATA))
            unnkey_error = True
        elif db[KEY_METADATA][KEY_METADATA_TYPE] != VALUE_METADATA_TYPE:
            log.warning("\"{0}\":\"{1}\" is not \"{2}\".".format(
                KEY_METADATA, KEY_METADATA_TYPE, VALUE_METADATA_TYPE))
            unnkey_error = True
        # delay raising these keys

        # check the necessary keys
        key_error = False
        if KEY_NAME_PATTERN not in db:
            log.error("\"{0}\" is not in JSON.".format(KEY_NAME_PATTERN))
            key_error = True

        if KEY_ARGUMENTS not in db:
            log.error("\"{0}\" is not in JSON.".format(KEY_ARGUMENTS))
            key_error = True

        if key_error:
            log.error("Error in checking the keys in \"{0}\"".format(json_path))
            raise Exception("Key check error.")

        # debug the information
        log.info("\"{0}\" is \"{1}\"".format(KEY_NAME_PATTERN, 
            db[KEY_NAME_PATTERN]))
        log.info("Number of arguments is {1}.".format(KEY_ARGUMENTS, 
            len(db[KEY_ARGUMENTS])))

        # check the arguments
        arg_error = False
        for k in db[KEY_ARGUMENTS]:
            v = db[KEY_ARGUMENTS][k]

            if KEY_ARG_DEFAULT not in v:
                log.warning("\"{0}\" missing from argument \"{1}\".".format(
                    KEY_ARG_DEFAULT, k))
                unnkey_error = True
            if KEY_ARG_TYPE not in v:
                log.warning("\"{0}\" missing from argument \"{1}\".".format(
                    KEY_ARG_TYPE, k))
                unnkey_error = True
            if KEY_ARG_LABEL not in v:
                log.warning("\"{0}\" missing from argument \"{1}\".".format(
                    KEY_ARG_LABEL, k))
                unnkey_error = True

            # report values
            if KEY_ARG_VALUES not in v:
                log.error("Values are missing from argument \"{0}\".".format(k))
                arg_error = True
            else:
                log.info("Arguments for \"{0}\" are {1}.".format(k,
                    v[KEY_ARG_VALUES]))

        if arg_error:
            log.error("Missing values for arguments.")
            raise Exception("Missing values for arguments.")

        # check the files
        if not quick:
            n_files = 0
            total_files = 0
            files = get_iterator(db_path, json_path)
            next(files)
            for row in files:
                total_files = total_files + 1
                if not os.path.isfile(os.path.join(db_path, row[-1])):
                    log.error("File \"{0}\" is missing.".format(row[-1]))
                    file_error = True
                else:
                    n_files = n_files + 1

            if n_files != total_files:
                log.error("Only {0} files out of {1} were found.".format(
                    n_files, total_files))
                raise Exception("Files were missing from the database.")
            else:
                log.info("{0} files validated to be present.".format(n_files))
        else:
            log.info("Doing a quick check. Not checking files.")

        # delay raising
        if unnkey_error:
            log.error("Error in checking the keys in \"{0}\"".format(json_path))
            raise Exception("Missing meta-data (but it may work as a Spec A).")
    except Exception as e:
        log.error("Check failed. \"{0}\" is invalid. {1}".format(db_path, e))
        return False

    log.info("Check succeeded.")
    return True

