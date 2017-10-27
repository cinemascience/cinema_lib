"""
Cinema Spec D utility functions for reading and validating databases.
"""

import sqlite3
import os
import logging as log
import csv
from functools import reduce
import hashlib
import time

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

# The python CSV reader mostly does RFC-4180 correctly on strict mode
# EXCEPT it won't detect a " after comma and white-space. This checks it.
def __python_rfc_4180_bug_check(row):
    for col in row:
        s = col.strip()
        if len(s) > 0 and col != s and s[0] == '"':
            return True
    return False

def get_iterator(db_path, csv_path=SPEC_D_CSV_FILENAME, strict=False):
    """
    Return a row iterator, assuming a valid Spec D database. Does
    not validate that it is a proper Spec D database, unless *strict*
    is *True*. The CSV file must adhere to RFC-4180 for proper 
    interpretation. If *strict* is True, it will raise an Exception on 
    parsing errors.

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV
        strict : boolean = False
            enable strict checking mode, and raise an error if it
            does not match RFC-4180

    returns:
        an iterator that returns a tuple of data per row if the csv_path 
        file can be opened, otherwise returns None

        the first row will be the header (column identifiers)

    raises:
        an exception during iteration if the file does not match the
        RFC-4180 specification

    TODO:
        properly type the exception as the same exception that csv.reader uses
    """

    fn = os.path.join(db_path, csv_path)
    if os.path.isfile(fn):
        # by default the Python CSV reader implements RFC-4180
        # with the exception that it doesn't detect double-quote after
        # comma and white-space (which is an error according to the spec)
        wrapped = None
        if strict:
            def __wrapped(fn):
                with open(fn, "r") as f:
                    for row in csv.reader(f, strict=True):
                        if __python_rfc_4180_bug_check(row):
                            raise Exception("Unescaped double-quote appears after comma and white-space.")
                        yield tuple(row)
            wrapped = __wrapped
        else:
            def __wrapped(fn):
                with open(fn, "r") as f:
                    for row in csv.reader(f):
                        yield tuple(row)
            wrapped = __wrapped
        return wrapped(fn)
    else:
        return None

def typecheck(values, nans=[]):
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

def typematch(row, types):
    """
    Given a row, will determine if the types match the header types,
    accounting for NaNs. In particular, it will allow NaN to be OK
    for both TYPE_STRING and TYPE_FLOAT.

    arguments:
        row : iterator of values

        header : iterator of types (TYPE_INTEGER, TYPE_FLOAT, or TYPE_STRING)

    returns:
        True if the types match, False if not
    """
    return reduce(lambda x, y: x and y, 
                  [t == h or (v.lower() == "nan" and h == TYPE_STRING)
                   for v, t, h in zip(row, typecheck(row), types)],
                  True)

def file_columns(header):
    """
    Given a header row, return the list of FILE column indices. Does
    not validate that they are in the right order, nor does it validate
    rows if they are strings or files.

    arguments:
        row : iterator of header identifiers

    returns:
        tuple of column indices that are FILEs
    """

    return [i for i, h in zip(range(0, len(header)), header) if
            h == FILE_HEADER_KEYWORD]


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
        log.info("Opening CSV file \"{0}\".".format(csv_path))
        reader = get_iterator(db_path, csv_path, True)
        if reader == None:
            log.error("Error opening \"{0}\".".format(csv_path))
            raise Exception("Error opening \"{0}\".".format(csv_path))

        # read the header
        try:
            header = next(reader)
        except Exception as e:
            log.error("Fatal error parsing header.")
            raise e

        log.info("Header is {0}.".format(header))
        columns = len(header)
        log.info("Number of columns are {0}.".format(len(header)))
        types = typecheck(header)

        # check the types of the first line
        header_error = reduce(lambda x, y: x or (y != TYPE_STRING), 
                              types, False)
        if header_error:
            log.error("Column header(s) are not all type string: {0}.".format(
                      types))

        # check if there is whitespace
        warn_whitespace = reduce(lambda x, y: x or (y[0] != y[1]),
                                 zip(header, [i.strip() for i in header]),
                                 False)
        if warn_whitespace:
            log.warning(
              "There are whitespace(s) preceeding or following a comma(s) in the header: {0}.".format(header))

        # check if there is FILE with whitespace
        warn_file_whitespace = reduce(lambda x, y: x or 
                                      ((y[1] == FILE_HEADER_KEYWORD) and 
                                       (y[0] != y[1])),
                                      zip(header, [i.strip() for i in header]),
                                      False)
        if warn_file_whitespace:
            log.warning(
              "There are whitespace(s) for FILE column(s) in the header. These will not be detected as proper FILEs: {0}.".format(header))

        # read the first line and types
        try:
            row = next(reader)
        except Exception as e:
            log.error("Fatal error parsing first data row.")
            raise e

        log.info("First data row is {0}.".format(row))
        types = typecheck(row)
        log.info("Data types are {0}.".format(types))
        if len(types) != len(header):
            log.error(
                "Number of columns in header and first row do not match.")
            header_error = True

        # check FILE
        files = file_columns(header)
        log.info("FILE column indices are {0}.".format(files))
        if len(files) > 0:
            for i in files:
                if i >= len(types):
                    log.error("FILE column #{0} is greater than the number of data columns {1} on row #1.".format(i, len(types)))
                    header_error = True
                elif types[i] != TYPE_STRING:
                    log.error("FILE column {0} is not string.".format(i))
                    header_error = True
            if files[-1] != len(row) - 1:
                log.error(
                    "FILE on column #{0} is not on the last column.".format(
                        files[-1]))
                header_error = True
            for i, j in zip(files[:-1], files[1:]):
                if j - i != 1:
                    log.error(
                    "FILE on column #{0} is not sequentially last.".format(
                        i))
                    header_error = True
        # delay the raise, because we can try to check rows

        # check the rows if we aren't doing a quick check
        if not quick:
            # reopen the reader because we are lazy and skip the header
            reader = get_iterator(db_path, csv_path, True)
            next(reader)

            row_error = False
            n_rows = 1
            n_files = 0
            total_files = 0
            try:
                for row in reader:
                    if len(header) != len(row):
                        log.error("On row #{0}: {1}".format(n_rows, row)) 
                        log.error("Unequal number of columns.")
                        row_error = True
                    if not typematch(row, types):
                        log.error("On row #{0}: {1}".format(n_rows, row)) 
                        log.error("Types do not match: {0}".format(typecheck(row)))
                        row_error = True

                    # check if there is whitespace
                    warn_whitespace = reduce(lambda x, y: x or (y[0] != y[1]),
                                             zip(row, 
                                                 [i.strip() for i in row]),
                                             False)
                    if warn_whitespace:
                        log.warning("On row #{0}: {1}".format(n_rows, row))
                        log.warning("There are whitespace(s) preceeding or following a comma(s).")

                    # check the files
                    for i in files:
                        if i < len(row):
                            total_files = total_files + 1
                            fn = os.path.join(db_path, row[i])
                            if not os.path.isfile(fn):
                                log.error("Error on row #{0}: {1}".format(n_rows, row)) 
                                log.error("File \"{0}\" is missing.".format(fn))
                                row_error = True
                            else:
                                n_files = n_files + 1
                        else:
                            log.error("Unable to check file on row #{0}, not enough columns.".format(n_rows))
                            row_error = True
                    # increment
                    n_rows = n_rows + 1
            except Exception as e:
                log.error("Fatal error parsing row #{0}.".format(n_rows))
                raise e

            log.info("Number of data rows are {0}.".format(n_rows - 1))
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
        files = file_columns(header)
        if len(files) > 0:
            log.info(
                "More than one FILE, so numbers will be appended to FILE.")
            header = list(header)
            for i, n in zip(files, range(0, len(files))):
                header[i] = header[i] + str(n)

        # figure out the table name
        name = os.path.splitext(os.path.basename(db_path))[0]
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
        db.commit()

        # done!
        log.info("Insertion of data into \"{0}\" was successful.".format(name))
        return db
    except Exception as e:
        log.error("Error in creating database: {0}.".format(e))
        return None

def move_to_backup(db_path, csv_path=SPEC_D_CSV_FILENAME):
    """
    Rename the CSV in a Spec D database to a backup name.

    arguments:
        db_path : string
            POSIX path to Cinema database
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV

    returns:
        the relative filename of the renamed csv_path

    side effects:
        renames old csv_path to csv_path.<epoch timestamp>.<md5 hash>
    """

    # calculate the hash and time stamp
    h = hashlib.md5()
    with open(os.path.join(db_path, csv_path)) as f:
        line = f.read(4096)
        while line != '':
            h.update(line.encode('utf-8'))
            line = f.read(4096)
        h = h.hexdigest()
    t = int(time.time())

    # get the paths
    full_fn = os.path.join(db_path, csv_path)
    backup = csv_path + '.' + str(t) + '.' + h
    full_backup = os.path.join(db_path, backup) 
    os.rename(full_fn, full_backup)

    return backup

def add_columns_by_row_data(db_path, column_names, row_function, 
                           csv_path=SPEC_D_CSV_FILENAME):
    """
    For every row in a Cinema database, it will evaluate *row_function*
    on the database (passing the row data to the function). This adds new
    column(s) to the database, by writing a new SPEC_D_CSV_FILENAME. 
    It will backup the old SPEC_D_CSV_FILENAME.

    arguments:
        db_path : string
            POSIX path to Cinema database
        column_names : tuple of strings
            the header name(s) for the new column(s). if a column name is FILE,
            the column will be appended to the total list of columns, otherwise
            it will be placed immediately before other FILE columns
        row_function : function(row: tuple of strings) => tuple of string
            a function that takes a row tuple, and returns a tuple of strings
            based on the row tuple, i.e., it will take the value of the
            row to compute new value(s). len of the return value must
            equal the len of column_names
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV

    returns:
        the name of the backup (previous version) csv_path

    side effects:
        writes a new csv_path and will rename the old csv_path to 
        csv_path.<epoch timestamp>.<md5 hash>
    """

    # create a backup
    backup = move_to_backup(db_path, csv_path)
    full_fn = os.path.join(db_path, csv_path)

    # get the data from the backup
    rows = get_iterator(db_path, backup) 
    header = next(rows)

    # calculate where to put the new columns
    is_file = [i == FILE_HEADER_KEYWORD for i in header + column_names]

    # create a row writing function
    # TODO we could be fancy and to vectorization (i.e., scan sum to swizzle)
    def write_row(writer, new_row):
        file_data = []
        non_file_data = []
        for t, d in zip(is_file, new_row):
            if t:
                file_data.append(d)
            else:
                non_file_data.append(d)
        writer.writerow(non_file_data + file_data)

    # write the new column data
    with open(full_fn, "w") as out:
        writer = csv.writer(out)
        # write the new header
        write_row(writer, header + column_names)
        # write the new rows
        for row in rows:
            write_row(writer, row + row_function(row))

    # return the backup filename
    return backup

def add_column_by_row_data(db_path, column_name, row_function, 
                           csv_path=SPEC_D_CSV_FILENAME):
    """
    For every row in a Cinema database, it will evaluate *row_function*
    on the database (passing the row data to the function). This adds a new
    column to the database, by writing a new SPEC_D_CSV_FILENAME. 
    It will backup the old SPEC_D_CSV_FILENAME. This is a convenience
    function that calls add_columns_by_row_data.

    arguments:
        db_path : string
            POSIX path to Cinema database
        column_name : string
            the header name for the new column. if the column name is FILE,
            the column will be appended to the total list of columns, otherwise
            it will be placed immediately before other FILE columns
        row_function : function(row: tuple of strings) => string
            a function that takes a row tuple, and returns a string
            based on the row tuple, i.e., it will take the value of the
            row to compute a new value.
        csv_path : string = SPEC_D_CSV_FILENAME
            POSIX relative path to Cinema CSV

    returns:
        the name of the backup (previous version) file

    side effects:
        writes a new SPEC_D_CSV_FILENAME and will rename the old 
        SPEC_D_CSV_FILENAME to SPEC_D_CSV_FILENAME.<epoch timestamp>.<md5 hash>
    """

    def __row_function(row):
        return (row_function(row),)

    return add_columns_by_row_data(db_path, (column_name,), __row_function,
                                   csv_path)
