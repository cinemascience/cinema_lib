"""
Specification D functions and utilities for reading and validating databases.
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

## TODO REMOVE
log.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=log.DEBUG, datefmt='%I:%M:%S')

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
        list of types (TYPE_INTEGER, TYPE_FLOAT, TYPE_STRING, or TYPE_FILE)
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
                    log.error("File \"{0}\" is missing.".format(fn))
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

#### TODO To fix

def __generate_results(self, index, values, fieldnames, inputJson):
    results = []
    for val in inputJson["arguments"][fieldnames[index]]["values"]:
        values[fieldnames[index]] = val
        if index == len(fieldnames)-1:
            # print values
            results.append(copy.copy(values))
        else:
            results += (this.__generate_results(index+1,
                            copy.copy(values),fieldnames, inputJson))
    return results


# ----------------------------------------------------------------------
#
#
#
# ----------------------------------------------------------------------
def convert_atod(self, inputDB, newDB): 
    # check that the new DB path is valid and doesn't exist
    newDB = newDB.rstrip("/")
    baseFile, extension = os.path.splitext(newDB)
    if extension != ".cbd":
        # add cdb extension
        newDB = newDB + ".cdb"

    # check output path and create; exit if error
    if os.path.isdir( newDB ):
        log.warning("Output database {0} already exists.".format(newDB))
        exit(1)

    log.info("Creating new Cinema database at {0}".format(newDB))

    try:
            os.mkdir(OUTPUT_DIRECTORY)
    except OSError as exc:
            if exc.errno != errno.EEXIST:
                    raise
            pass
    
    jsonFile = os.path.join(inputDB, "image", "info.json") 
    inputJson = None
    with open(jsonFile) as f:
        inputJson = json.load(f)
    
        # get fieldnames (parameters) from JSON
        fieldnames = []
        for arg in inputJson["arguments"]:
            fieldnames.append(str(arg))
        
        # Write csv and copy images
        csvFileName = os.path.join( newDB, 'data.csv')
        with open(csvFileName, 'w+') as csvfile:
            namePattern = str(inputJson["name_pattern"])
            newExt = os.path.splitext(namePattern)[1]
            
            # get results
            values = {}
            results = this.__generate_results(0, {}, fieldnames, inputJson)
            
            # we have to add one more fieldname, specific to the conversion
            fieldnames.append("FILE")
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            newFileID = 0
            for result in results:
                pattern = copy.copy(namePattern)
                for dimension in result.iterkeys():
                    pattern = pattern.replace('{'+dimension+'}',
                                str(result[dimension]))
                # If an image for the result exists, copy it to output
                # and write a line to the csv
                if os.path.exists(os.path.join(inputDB, pattern)):
                    src = os.path.join(inputDB, pattern)
                    newFileID += 1
                    newFileName = str(newFileID)+str(newExt)
                    dst = os.path.join(newDB, newFileName) 
                    copyfile(src,dst)
                    result["FILE"] = newFileName
                    writer.writerow(result)
            log.info("Done converting database")

#           except IOError:
#               log.warning("Cannot open csv file {0}".format(csvFileName))
             
#       except IOError:
#           log.warning("Cannot open json file {0}".format(jsonFile))
