"""
Cinema Specification utility functions.
"""

from .d import SPEC_D_CSV_FILENAME
from .a import SPEC_A_JSON_FILENAME
from .a import get_dictionary
from .a import get_iterator
from .a import KEY_ARGUMENTS
from .d import FILE_HEADER_KEYWORD

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

    db = get_iterator(db_path)
    if db == None:
        log.error("Unable to open \"{0}\" in \"{1}\".".format(
            SPEC_A_JSON_FILENAME, db_path))
        return False
   
    # create the csv 
    try:
        with open(csv_fn, "w") as f:
            # iterate over the data
            for row in db:
                line = ""
                for col in row[:-1]:
                    line = line + str(col) + ","
                line = line + str(row[-1]) + "\n"
                f.write(line)
    except Exception as e:
        log.error("Conversion of database failed with \"{0}\".".format(e))
        return False

    return True

