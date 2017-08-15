"""
Specification A functions and utilities for reading and validating databases.
"""

import json
import os

SPEC_A_JSON_FILENAME = "info.json"

def get_dictionary(db_path, json_path=SPEC_A_JSON_FILENAME):
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

    json_fn = os.path.join(db_path, json_path)
    if not os.path.exists(json_fn):
        return False
   
    try:
        with open(json_fn) as jf:
            return json.load(jf)
    except:
        return None

