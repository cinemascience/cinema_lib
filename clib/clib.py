from . import spec
from .spec import d
import os

# ---------------------------------------------------------------------------
#
# check a database, and return the type and version number of the database
#
# ---------------------------------------------------------------------------
def check_database( dbname ):
    res = [spec.CinemaSpec.CINEMA_INVALID_DATABASE, "0.0"]

    spec_d = specd.CinemaSpecD()

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

