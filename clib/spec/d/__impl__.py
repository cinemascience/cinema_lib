"""
Cinema Spec D utility functions for reading and validating databases.
"""

import sqlite3
import os
import logging as log
import csv
from functools import reduce

SPEC_D_CSV_FILENAME = "data.csv"
FILE_HEADER_KEYWORD = "FILE"
TYPE_INTEGER = "INTEGER"
TYPE_FLOAT = "FLOAT"
TYPE_STRING = "STRING"
CDB_TO_SQLITE3 = {
    TYPE_INTEGER: "INTEGER",
    TYPE_FLOAT: "REAL",
    TYPE_STRING: "TEXT"
    }

def get_iterator(db_path, csv_path=SPEC_D_CSV_FILENAME):
    """
    Return a row iterator, assuming a valid Spec D database. Does
    not validate that it is a proper Spec D database. 

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV

    returns:
        an iterator that returns a tuple of data per row if the csv_path 
        file can be opened, otherwise returns None

        the first row will be the header (column identifiers)
    """

    reader = None
    fn = os.path.join(db_path, csv_path)

    if os.path.isfile(fn):
        f = open(fn, "r") 
        reader = csv.reader(f, delimiter=",", doublequote=False, 
                     escapechar=None)

        def wrapped(reader):
            for row in reader:
                yield tuple([col.strip() for col in row])

        reader = wrapped(reader)

    return reader

def typecheck(values):
    """
    Return a tuple of Spec D types given an iterator of strings.

    arguments:
        values : iterator of strings
    
    returns:
        tuple of types (TYPE_INTEGER, TYPE_FLOAT, or TYPE_STRING)
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
    return tuple(types)

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

    log.info("Checking database \"{0}\" as Spec D.".format(db_path))
    try:
        # get the reader
        reader = get_iterator(db_path, csv_path)
        if reader == None:
            log.error("Error opening \"{0}\".".format(csv_path))
            raise Exception("Error opening \"{0}\".".format(csv_path))

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
        if len(types) != len(header):
            log.error(
                "Number of columns in header and first row do not match.")
            header_error = True
        # check FILE
        files = [i for i, t, h in zip(range(0, len(types)), types, header) if
                 h == FILE_HEADER_KEYWORD]
        log.info("FILE column indices are {0}.".format(files))
        if files[-1] != len(types) - 1:
            log.warning("FILE(s) are not on the last column(s).")
            header_error = True
        for i, j in zip(files[:-1], files[1:]):
            if j - i != 1:
                log.warning("FILE(s) are not on the last column(s).")
                header_error = True
        for i in files:
            if types[i] != TYPE_STRING:
                log.error("FILE column {0} is not string.".format(i))
                header_error = True
        # delay the raise, because we can try to check rows

        # check the rows if we aren't doing a quick check
        if not quick:
            # reopen the reader because we are lazy and skip the header
            reader = get_iterator(db_path, csv_path)
            next(reader)

            row_error = False
            n_rows = 0
            n_files = 0
            total_files = 0
            for row in reader:
                n_rows = n_rows + 1
                if len(header) != len(row):
                    log.error(
                      "Unequal number of columns on row #{0}.".format(n_rows))
                    row_error = True
                if not reduce(lambda x, y: x and y, 
                              [a == b or 
                                  (a.lower() == "nan" and b == TYPE_STRING)
                                  for a, b in zip(typecheck(row), types)],
                              True):
                  log.error("Types do not match on row #{0}:".format(n_rows))
                  row_error = True
                # check the files
                for i in files:
                    total_files = total_files + 1
                    fn = os.path.join(db_path, row[i])
                    if not os.path.exists(fn):
                        log.error(
                          "File \"{0}\" on row #{1} is missing.".format(fn, 
                              n_rows))
                        row_error = True
                    else:
                        n_files = n_files + 1

            log.info("Number of rows are {0}.".format(n_rows))
            if n_files != total_files:
                log.error("Only {0} files out of {1} were found.".format(
                    n_files, total_files))
            else:
                log.info("{0} files validated to be present.".format(n_files))

            if row_error:
                raise Exception("Error checking rows.")
        else:
            log.info("Doing a quick check. Not checking row data.")

        # raise is delayed
        if header_error:
            raise Exception("Error checking header and types.")
    except Exception as e:
        log.error("Check failed. \"{0}\" is invalid. {1}".format(db_path, e))
        return False

    log.info("Check succeeded.")
    return True

def get_sqlite3(db_path, csv_path=SPEC_D_CSV_FILENAME, where=":memory:"):
    """
    Returns a SQLite3 database that backs a Spec D database. Does not check 
    that the database is valid. By default, will open an in-memory SQLite3,
    and will be temporary.

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV
        where : string = ":memory:"
            where to back the SQLite3 on disk; ":memory:" is temporary in 
            memory
            
    returns:
        a SQLite3 database if successful, None if not. The table that
        backs the sqlite3 will be named by the base filename of *db_path*,
        i.e., if the database is "/home/foo/bar.cdb/" the table will be
        named "bar".

        strings will be text columns, floats will be real columns, and
        integers will be integer columns. Column names will be determined
        by the CSV headers.

    side-effects:
        will open a file on disk at *where* if given a POSIX path or URI

        logs results to the logger for information and debugging
    """

    log.info("Converting \"{0}/{1}\" into a SQLite database at \"{2}\".".
        format(db_path, csv_path, where))

    try:
        # open the sqlite3
        db = sqlite3.connect(where)
        cursor = db.cursor()

        # open the cinema db
        cdb = get_iterator(db_path, csv_path)

        # get the header and first row
        header = next(cdb)
        log.info("Header is {0}.".format(header))
        first = next(cdb)
        log.info("First row is {0}.".format(first))
        types = typecheck(first)
        log.info("Types are {0}.".format(types))

        # determine if we have more than one FILE
        # and adjust names
        files = [i for i, t, h in zip(range(0, len(types)), types, header) if
                 h == FILE_HEADER_KEYWORD]
        if len(files) > 0:
            log.info(
                "More than one FILE, so numbers will be appended to FILE.")
            for i in files:

        # figure out the table name
        name = os.path.splitext(os.path.basename(os.path.dirname(db_path)))[0]
        log.info("Table name is \"{0}\".".format(name))

        # create the table
        create = "CREATE TABLE \"{0}\" (".format(name)
        for h, t in zip(header, types):
            create = create + "\"" + h + "\" " + CDB_TO_SQLITE3[t] + ","
        create = create[:-1] + ")"
        log.info("Create table string is \"{0}\".".format(create))
        cursor.execute(create)

        # insert the data
        insert = "INSERT INTO \"{0}\" VALUES (%s)".format(name) % \
                 ",".join("?"*len(first))
        log.info("Insert string is \"{0}\".".format(insert))
        cursor.execute(insert, first)
        cursor.executemany(insert, cdb)

        # done!
        log.info("Insertion of data into \"{0}\" was successful.".format(name))
        return db
    except Exception as e:
        log.error("Error in creating database: {0}.".format(e))
        return None

