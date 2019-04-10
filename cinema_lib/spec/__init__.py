"""
Cinema Specification utility functions.
"""

from ..spec import d 
from ..spec import a

import os
import logging as log

CINEMA_DATABASE_EXT = ".cdb"

def convert_a_to_d(db_path):
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

    csv_fn = os.path.join(db_path, d.SPEC_D_CSV_FILENAME)
    if os.path.exists(csv_fn):
        log.error("{0} exists. Refusing to execute.".format(csv_fn))
        return False
    
    # special case to handle incorrectly written Spec A databases from ParaView
    use_imagedir = False
    db = a.get_iterator(db_path)
    if db == None:
        # ParaView writes the info.json file here ...
        db = a.get_iterator(db_path,"image/info.json")
        if db == None:
            log.error("Unable to open \"{0}\" in \"{1}\".".format(
                a.SPEC_A_JSON_FILENAME, db_path))
            return False
        else:
            use_imagedir = True 

    # create the csv 
    try:
        with open(csv_fn, "w") as f:
            # iterate over the data
            firstline = True
            for row in db:
                line = ""
                for col in row[:-1]:
                    line = line + str(col) + ","

                # ParaView exception logic 
                if use_imagedir:
                    if firstline:
                        line = line + str(row[-1]) + "\n"
                        firstline = False
                    else:
                        line = line + "image/" + str(row[-1]) + "\n"
                else:
                    line = line + str(row[-1]) + "\n"

                f.write(line)

    except Exception as e:
        log.error("Conversion of database failed with \"{0}\".".format(e))
        return False

    return True

