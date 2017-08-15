"""
Cinema Spec D utility functions for reading and validating databases.
"""

import os
import logging as log
import csv
from functools import reduce

SPEC_D_CSV_FILENAME = "data.csv"
FILE_HEADER_KEYWORD = "FILE"
TYPE_INTEGER = "INTEGER"
TYPE_FLOAT = "FLOAT"
TYPE_STRING = "STRING"

def get_iterator(db_path, csv_path=SPEC_D_CSV_FILENAME):
    """
    Return a row iterator, assuming a valid Spec A database. Does
    not validate that it is a proper Spec D database. 

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV

    returns:
        an iterator that returns a list of columns per row, which
        is open to the Cinema CSV if the csv_path file can be opened, 
        otherwise returns None
    """

    reader = None
    fn = os.path.join(db_path, csv_path)

    if os.path.isfile(fn):
        f = open(fn, "r") 
        reader = csv.reader(f, delimiter=",", doublequote=False, 
                     escapechar=None)

        def wrapped(reader):
            for row in reader:
                yield [col.strip() for col in row]

        reader = wrapped(reader)

    return reader

def typecheck(values):
    """
    Return a list of Spec D types given a list of strings.

    arguments:
        values : list of strings
    
    returns:
        list of types (TYPE_INTEGER, TYPE_FLOAT, or TYPE_STRING)
    """

    types = []
    for v in values:
        try:
            test = int(v)
            types.append(TYPE_INTEGER)
        except:
            try:
                test = float(v.lower())
                types.append(TYPE_FLOAT)
            except:
                types.append(TYPE_STRING)
    return types

def check_database(db_path, csv_path=SPEC_D_CSV_FILENAME, quick=False):
    """
    Validate a Spec D database.

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV
        quick : boolean = False
            if True, perform a quick check, which means only checking
            the first two lines

    returns:
        True if it is valid, False otherwise

    side effects:
        logs error and info messages to the logger
    """

    res = True

    log.info("Checking database \"{0}\" as Spec D.".format(db_path))
    try:
        # get the reader
        reader = get_iterator(db_path, csv_path)
        if reader == None:
            log.error("CSV \"{0}\" does not exist.".format(csv_path))
            raise 

        # read the header
        header = next(reader)
        log.info("Header is {0}.".format(header))
        columns = len(header)
        log.info("Number of columns are {0}.".format(len(header)))

        # read the first line and types
        header_error = False
        row = next(reader)
        log.info("First data row is {0}.".format(row))
        types = typecheck(row)
        log.info("Data types are {0}.".format(types))
        # check FILE
        files = [i for i, t, h in zip(range(0, len(types)), types, header) if
                 h == FILE_HEADER_KEYWORD]
        log.info("FILE column indices are {0}.".format(files))
        if files[-1] != len(types) - 1:
            log.error("FILE(s) are not on the last column(s).")
            header_error = True
        for i, j in zip(files[:-1], files[1:]):
            if j - i != 1:
                log.error("FILE(s) are not on the last column(s).")
                header_error = True
        for i in files:
            if types[i] != TYPE_STRING:
                log.error("FILE column {0} is not string.".format(i))
                header_error = True
        if header_error:
            raise Exception("Error checking FILE and types.")

        # check the rows if we aren't doing a quick check
        if not quick:
            # reopen the reader because we are lazy and skip the header
            reader = get_iterator(db_path, csv_path)
            next(reader)

            row_error = False
            n_rows = 0
            n_files = 0
            for row in reader:
                n_rows = n_rows + 1
                if len(header) != len(row):
                    log.error(
                      "Unequal number of columns on row #{0}.".format(n_rows))
                    row_error = True
                if not reduce(lambda x, y: x and y, 
                              [a == b for a, b in zip(typecheck(row), types)],
                              True):
                  log.error("Types do not match on row #{0}:".format(n_rows))
                  row_error = True
                # check the files
                for i in files:
                    fn = os.path.join(db_path, row[i])
                    if not os.path.exists(fn):
                        log.error(
                          "File \"{0}\" on row #{1} is missing.".format(fn, 
                              n_rows))
                        row_error = True
                    else:
                        n_files = n_files + 1

            if row_error:
                log.warning("Only {0} files were found.".format(n_files))
                raise Exception("Error checking rows.")
            else:
                log.info("{0} files validated to be present.".format(n_files))
                log.info("Number of rows are {0}.".format(n_rows))
        else:
            log.info("Doing a quick check. Not checking row data.")
    except Exception as e:
        log.error("Check failed. \"{0}\" is invalid. {1}".format(db_path, e))
        return False

    log.info("Check succeeded.")
    return True


