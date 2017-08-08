import os
import logging as log
import csv
import sqlite3

CINEMA_INVALID_DATABASE = "invalid"
CSV_FILENAME = "data.csv"

DB = ""


# ---------------------------------------------------------------------------
#
# set up the proper reporting mode
#
# use these calls as needed for reporting:
#
# log.info("verbose message") 
# log.warning("warning message") 
# log.error("error message") 
#
# ---------------------------------------------------------------------------
def init():
    log.basicConfig(format="%(levelname)s: %(message)s")

def set_verbose( verbose ):
    if verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Setting verbose output.")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
#
# return a csv reader with the correct grammar, delimiter, escape characters 
#
# INPUT: input is a valid open file
#
# ---------------------------------------------------------------------------
def get_csvreader( openfile ):
    return csv.reader( openfile, delimiter=",", 
                       doublequote=False, escapechar='\\')
   
# ---------------------------------------------------------------------------
#
# check a database, and return the type and version number of the database
#
# ---------------------------------------------------------------------------
def check_database( dbname ):
    res = [CINEMA_INVALID_DATABASE, "0.0"]
    if check_database_d( dbname ):
        res = ["D", "1.0"]
    return res

# ---------------------------------------------------------------------------
#
# check a database D v1.0 
#
# ---------------------------------------------------------------------------
def check_database_d( dbname ):
    res = True

    log.info("checking database {0} as Spec D".format(dbname))
    if os.path.isdir( dbname ):
        # does the csv file exist
        if os.path.isfile( os.path.join(dbname,CSV_FILENAME) ):
            with open( os.path.join(dbname,CSV_FILENAME), 'r' ) as csvfile:
                CSVReader = get_csvreader( csvfile )  
                numfields = 0
                isFirstLine = True
                hasFileField = False
                for row in CSVReader: 
                    if isFirstLine:
                        isFirstLine = False
                        numfields = len( row )
                        if row[-1] == "FILE":
                            hasFileField = True
                    else:
                        if len(row) == numfields:
                            if hasFileField: 
                                if not os.path.isfile(os.path.join(dbname, row[-1])):
                                    log.error("ERROR: File does not exist: {0}".format(row[-1]))
                                    res = False
                        else:
                            res = False 


        else:
            res = False
            log.error("required file {0} does not exist".format(CSV_FILENAME))
    else:
        res = False
        log.error("database {0} does not exist".format( dbname ))

    if res:
        log.info("Check succeeded: valid D database")
    return res
    

# ---------------------------------------------------------------------------
#
# load a csv file into a sqlite3 database
#
# ---------------------------------------------------------------------------
def load( fname):
    global DB = sqlite3.connect(":memory:")
    cur = DB.cursor()
    # construct the string to execute
    cur.execute("CREATE TABLE cdb (?,?,?,,,,)", row) 

    with open('data.csv','rb') as fin: # `with` statement available in 2.5+
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['col1'], i['col2']) for i in dr]

    cur.executemany("INSERT INTO t (col1, col2) VALUES (?, ?);", to_db)
    con.commit()
    con.close()

