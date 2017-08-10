import os
import logging as log
import csv
import cspec

class CinemaSpecD(cspec.CinemaSpec):
    CSV_FILENAME = "data.csv"

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
            log.info("check succeeded: valid D database")

        return res
        

    # -----------------------------------------------------------------------
    #
    # convert Spec A to Spec D 
    #
    # -----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    #
    # Recursively generate results for all possible combinations of parameters
    # Starts from the parameter at index, and uses values for the value of     
    # earlier parameters
    #
    # generate_results(0,{}) will generate ALL results for ALL parameters
    #
    # ----------------------------------------------------------------------
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
