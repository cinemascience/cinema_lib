"""
Specification A functions and utilities for reading and validating databases.
"""

import json

SPEC_A_JSON_FILENAME = "info.json"

def get_dictionary():
    """
    Return a JSON dictionary, assuming a valid Spec A database. Does
    not validate that it is a proper Spec A database. 

    arguments:
        db_path : string
            POSIX path to Cinema database
        json_path : string = SPEC_A_JSON_FILENAME
            POSIX relative path to Cinema JSON 

    returns:
        a dictionary of the contents of the Cinema JSON if the file can
        be opened, otherwise returns None
    """

    pass

