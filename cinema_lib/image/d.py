"""
Row functions for processing image data in Cinema D.
"""

from ..spec import d

from skimage import io

import os
import logging as log


# TODO rename to columns
def file_add_column(db_path, column_number,
                    function_name, image_function,
                    csv_path=d.SPEC_D_CSV_FILENAME,
                    n_components=None,
                    fill="NaN"):
    """
    Adds a new column(s) to a Spec D database. Given a function that returns
    a list, array or tuple of values, it will determine the vector length
    that image_function returns if n_components is None by reading the
    the first image in the database. If n_components is >= 0, then 
    image_function must return a vector of the same length (returns a
    scalar if n_components is 0). It adds a number of columns to the
    database based on n_components, where it will add 1 for 0 components.

    arguments:
        db_path : string
            POSIX path to a Cinema Spec D database
        column_number : integer >= 0
            FILE column that contains the image files
        function_name : string
            the header(s) that will be added to the database. must be
            "FILE" if image_function is adding new files to the database
        image_function : function(db_path : string, image_path : string) =>
            tuple of n_components if n_components >= 1 else a value

                a function that takes 2 arguments, the path to a Cinema
            database and a relative path to an image. it returns a tuple
            of values with length equal to the number of components of the 
            input image if n_components is None, otherwise it returns
            a tuple of values of length specified by n_components 
            (or just a value if n_components is 0)
        csv_path : string = d.SPEC_D_CSV_FILENAME
            the relative POSIX path to data.csv (or otherwise named)
        n_components : integer = None
            the number of components (vector length) that image_function
            will return. if None, will read the first image in the database
            and it is assumed that image_function will return the same
            number of components.
        fill : string = "NaN"
            the replacement value if the image_function raises an exception
            and does not return a value - will be turned into a vector
            of length n_components

    returns:
        a boolean, True if there was an error and no changes were made
        to the database, and False if the database was updated
    """

    # get the first image
    data = d.get_iterator(db_path, csv_path)
    next(data)
    row = next(data)
    im = io.imread(os.path.join(db_path, row[column_number]))
    # close the file
    del data

    if not (len(im.shape) == 2 or len(im.shape) == 3):
        log.error("Unsupported image dimensions: {0}.".format(im.shape))
        return True

    # determine the number of components
    if n_components == None:
        if len(im.shape) == 3:
            n_components = im.shape[2]
        else:
            n_components = 0

    # create new column names
    column_names = (function_name,)
    if n_components > 0:
        column_names = tuple([function_name + " " + str(i) for i in
                              range(0, n_components)])

    # iterate over the rows
    d.add_columns_by_row_data(db_path, column_names,
                              d.file_row_function(db_path, column_number, n_components,
                                                  function_name, image_function, fill),
                              csv_path=csv_path)
    return False
