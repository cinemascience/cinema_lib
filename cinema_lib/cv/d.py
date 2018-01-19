"""
Row functions for processing image data in Cinema D.
"""

from ..spec import d

import os
import logging as log

# TODO rename to columns
def file_add_file_column(db_path, column_number, 
                         function_name, cv_function,
                         csv_path=d.SPEC_D_CSV_FILENAME,
                         fill=""):
    """
    Adds a new FILE column(s) to a Spec D database. Given a function that 
    returns a new filename.

    arguments:
        db_path : string
            POSIX path to a Cinema Spec D database
        column_number : integer >= 0
            FILE column that contains the image files
        function_name : string
            the header(s) that will be added to the database. must be
            "FILE" 
        cv_function : function(db_path : string, image_path : string) => string

                a function that takes 2 arguments, the path to a Cinema
            database and a relative path to an image. it returns a string
            that is the relative filename to the new file.
        csv_path : string = d.SPEC_D_CSV_FILENAME
            the relative POSIX path to data.csv (or otherwise named)
        fill : string = ""
            the replacement value if the file_function raises an exception
            and does not return a value

    returns:
        a boolean, True if there was an error and no changes were made
        to the database, and False if the database was updated
    """

    # create new column names
    column_names = (function_name,)

    # iterate over the rows
    d.add_columns_by_row_data(db_path, column_names,
      d.file_row_function(db_path, column_number, 0, 
                          function_name, cv_function, fill), 
                          csv_path=csv_path)
    return False


