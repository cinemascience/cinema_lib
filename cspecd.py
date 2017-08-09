import os
import logging as log
import csv
import cspec

class CinemaSpecD(cspec.CinemaSpec):
    CSV_FILENAME = "data.csv"
    CINEMA_INVALID_DATABASE = "invalid"

    def __init__(self):
        self.dbspec    = "N"
        self.dbversion = "0.0"

    def __del__(self):
        return

    # -----------------------------------------------------------------------
    #
    # return a csv reader w/correct grammar, delimiter, escape characters 
    #
    # -----------------------------------------------------------------------
    def __get_csvreader(self, csvfile ):
        reader = None

        if os.path.isfile(csvfile):
            openfile = open(csvfile, "r") 
            reader = csv.reader( openfile, delimiter=",", 
                           doublequote=False, escapechar='\\')
        else:
            log.warning("csvfile {0} does not exist",format(csvfile))

        return reader

    # -----------------------------------------------------------------------
    #
    # check a database D v1.0 
    #
    # -----------------------------------------------------------------------
    def check_database(self, dbname ):
        res = True

        log.info("checking database {0} as Spec D".format(dbname))
        if os.path.isdir( dbname ):
            # does the csv file exist
            reader = self.__get_csvreader(
                        os.path.join(dbname,self.CSV_FILENAME))

            if reader != None:
                numfields = 0
                isFirstLine = True
                hasFileField = False
                for row in reader: 
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
        
