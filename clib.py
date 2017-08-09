import os
import logging as log
import csv
import sqlite3
import cspec
import cspecd

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
# check a database, and return the type and version number of the database
#
# ---------------------------------------------------------------------------
def check_database( dbname ):
    res = [cspec.CinemaSpec.CINEMA_INVALID_DATABASE, "0.0"]

    spec_d = cspecd.CinemaSpecD()

    if spec_d.check_database( dbname ):
        res = ["D", "1.0"]
    return res

# ---------------------------------------------------------------------------
#
# load a csv file into a sqlite3 database
#
# ---------------------------------------------------------------------------
#def load( fname):
#   global DB = sqlite3.connect(":memory:")
#   cur = DB.cursor()
    # construct the string to execute
#   cur.execute("CREATE TABLE cdb (?,?,?,,,,)", row) 

#   with open('data.csv','rb') as fin: # `with` statement available in 2.5+
#       # csv.DictReader uses first line in file for column headings by default
#       dr = csv.DictReader(fin) # comma is default delimiter
#       to_db = [(i['col1'], i['col2']) for i in dr]

#   cur.executemany("INSERT INTO t (col1, col2) VALUES (?, ?);", to_db)
#   con.commit()
#   con.close()

