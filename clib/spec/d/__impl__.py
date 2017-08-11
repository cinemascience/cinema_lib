"""
Specification D functions and utilities for reading and validating databases.
"""

from ..a import SPEC_A_JSON_FILENAME

import os
import logging as log
import csv
from functools import reduce
from itertools import product
import json

SPEC_D_CSV_FILENAME = "data.csv"
FILE_HEADER_KEYWORD = "FILE"
TYPE_INTEGER = "INTEGER"
TYPE_FLOAT = "FLOAT"
TYPE_STRING = "STRING"

def get_csv_reader(db_path, csv_path=SPEC_D_CSV_FILENAME):
    """
    Return a csv reader, assuming a valid Spec D csv database.

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV

    returns:
        csv.reader that is open to the Cinema CSV if the csv_path file
        can be opened, otherwise returns None
    """

    reader = None
    fn = os.path.join(db_path, csv_path)

    if os.path.isfile(fn):
        f = open(fn, "r") 
        reader = csv.reader(f, delimiter=",", doublequote=False, 
                 escapechar=None)

    return reader

def csv_next(csv_reader):
    return [col.strip() for col in next(csv_reader)]

def csv_iterator(csv_reader):
    return ([col.strip() for col in row] for row in csv_reader)

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

def check_database(db_path, csv_path=SPEC_D_CSV_FILENAME):
    """
    Validate a Spec D database.

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV

    returns:
        True if it is valid, False otherwise

    side effects:
        logs error and info messages to the logger
    """

    res = True

    log.info("Checking database \"{0}\" as Spec D.".format(db_path))
    try:
        # get the reader
        reader = get_csv_reader(db_path, csv_path)
        if reader == None:
            log.error("CSV \"{0}\" does not exist.".format(csv_path))
            raise 

        # read the header
        header = csv_next(reader)
        log.info("Header is {0}.".format(header))
        columns = len(header)
        log.info("Number of columns are {0}.".format(len(header)))

        # read the first line and types
        row = csv_next(reader)
        log.info("First data row is {0}.".format(row))
        types = typecheck(row)
        log.info("Data types are {0}.".format(types))
        files = [i for i, t, h in zip(range(0, len(types)), types, header) if
                 h == FILE_HEADER_KEYWORD and t == TYPE_STRING]
        log.info("FILE column indices are {0}.".format(files))

        # reopen the reader because we are lazy and skip the header
        reader = get_csv_reader(db_path, csv_path)
        csv_next(reader)

        # check the rows
        row_error = False
        n_rows = 0
        n_files = 0
        for row in csv_iterator(reader):
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
                      "File \"{0}\" on row #{1} is missing.".format(fn, n_rows))
                    row_error = True
                else:
                    n_files = n_files + 1

        if row_error:
            log.warning("Only {0} files were found.".format(n_files))
            raise
        else:
            log.info("{0} files validated to be present.".format(n_files))
        log.info("Number of rows are {0}.".format(n_rows))
    except:
        log.error("Check failed. \"{0}\" is invalid.".format(db_path))
        return False

    log.info("Check succeeded.")
    return True

def convert_from_spec_a(db_path):
    """
    Create a Spec D CSV in a Spec A database.

    arguments:
        db_path : string
            POSIX path to a Cinema Spec A database

    returns:
        True if it was able to create it, False if not

    side effects:
        logs error and info messages to the logger
        writes out a SPEC_D_CSV_FILENAME at *db_path*
    """
    csv_fn = os.path.join(db_path, SPEC_D_CSV_FILENAME)
    if os.path.exists(csv_fn):
        log.error("{0} exists. Refusing to execute.".format(csv_fn))
        return False

    json_fn = os.path.join(db_path, SPEC_A_JSON_FILENAME)
    if not os.path.exists(json_fn):
        log.error("{0} does not exist.".format(json_fn))
        return False
   
    # create the csv 
    log.info("Creating new Spec D CSV at \"{0}\".".format(db_path))
    try:
        with open(json_fn) as jf, open(csv_fn, "w") as f:
            j = json.load(jf)
            # get the keys and write the header
            keylist = list(j['arguments'].keys())
            for col in keylist:
                f.write("{0},".format(col))
            f.write("FILE\n")
            # Cartesian product
            for row in product(*[i['values'] for i in 
                               j['arguments'].values()]):
                for col in row:
                    f.write("{0},".format(col))
                kv = {k: v for k, v in zip(keylist, row)}
                f.write(j['name_pattern'].format(**kv) + '\n')
    except Exception as e:
        log.error("Conversion of database failed with \"{0}\".".format(e))
        return False

    return True

