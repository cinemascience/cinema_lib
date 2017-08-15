"""
Cinema Specification utility functions.
"""

from .d import SPEC_D_CSV_FILENAME
from .a import SPEC_A_JSON_FILENAME
from .a import get_dictionary

import os
import logging as log
from itertools import product

CINEMA_DATABASE_EXT = ".cdb"

def convert_d_to_a(db_path):
    """
    Create a Spec D CSV, in place, in a Spec A database.

    arguments:
        db_path : string
            POSIX path to a Cinema Spec A database

    returns:
        True if it was able to create it, False if not

    side effects:
        logs error and info messages to the logger
        writes out a SPEC_D_CSV_FILENAME at *db_path*
    """

    log.info("Creating new Spec D CSV at \"{0}\".".format(db_path))

    csv_fn = os.path.join(db_path, SPEC_D_CSV_FILENAME)
    if os.path.exists(csv_fn):
        log.error("{0} exists. Refusing to execute.".format(csv_fn))
        return False

    db = get_dictionary(db_path)
    if db == None:
        log.error("Unable to open \"{0}\" in \"{1}\".".format(
            SPEC_A_JSON_FILENAME, db_path))
        return False
   
    # create the csv 
    try:
        with open(csv_fn, "w") as f:
            # get the keys and write the header
            keylist = list(db['arguments'].keys())
            for col in keylist:
                f.write("{0},".format(col))
            f.write("FILE\n")
            # Cartesian product
            for row in product(*[i['values'] for i in 
                               db['arguments'].values()]):
                for col in row:
                    f.write("{0},".format(col))
                kv = {k: v for k, v in zip(keylist, row)}
                f.write(db['name_pattern'].format(**kv) + '\n')
    except Exception as e:
        log.error("Conversion of database failed with \"{0}\".".format(e))
        return False

    return True

