from . import pillow_wrapper as pw
from . import error_calculation as ec
from . import error_statistics_calculation as es
from ..image import d as d_im_image
from ..cv import d as d_cv_image
import csv
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor


def calculate_uncertainty(db_path, column_number, csv_path="data.csv"):
    """
        Calculates all implemented uncertainty measures and creates database entries for them

        arguments:
            db_path : string
                POSIX path for the Cinema database

            column_number : integer >= 0
                FILE column that contains the image files

            csv_path : string = d.SPEC_D_CSV_FILENAME
                the relative POSIX path to data.csv (or otherwise named)

        side effects:
            writes out the uncertainty images
        """
    filenamelist = get_filenames_from_csv(os.path.join(db_path, csv_path), column_number)
    print("Running", len(filenamelist) * 7, "Jobs for", len(filenamelist), "Pictures")
    print("Using", multiprocessing.cpu_count(), "Threads")
    print((len(filenamelist) * 7) / multiprocessing.cpu_count(), "Jobs per Thread")

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        for i in filenamelist:
            try:
                pw.open_image(os.path.join(db_path, i))
            except IOError:
                print(os.path.join(db_path, i), "not found")
                continue

            executor.submit(calculate_uncertainty_salt_and_pepper, db_path, i)
            executor.submit(calculate_uncertainty_local_range, db_path, i)
            executor.submit(calculate_uncertainty_contrast_strech, db_path, i)
            executor.submit(calculate_uncertainty_acutance, db_path, i)
            executor.submit(calculate_uncertainty_gaussian, db_path, i)
            executor.submit(calculate_uncertainty_local_contrast, db_path, i)
            executor.submit(calculate_uncertainty_brightness, db_path, i)

    print("Writing rows")

    d_cv_image.file_add_file_column(db_path, column_number, "FILE_u_acutance", create_db_entry_uncertainty_acutance)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_u_gaussian", create_db_entry_uncertainty_gaussian)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_u_local_contrast",
                                    create_db_entry_uncertainty_local_contrast)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_u_local_range",
                                    create_db_entry_uncertainty_local_range)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_u_salt_and_pepper",
                                    create_db_entry_uncertainty_salt_and_pepper)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_u_brightness", create_db_entry_uncertainty_brightness)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_u_contrast_strech",
                                    create_db_entry_uncertainty_contrast_strech)

    print("Finished uncertainty quantification")


def add_image_function_columns(db_path, imagefunction, prefix, csv_path="data.csv", file_pre="FILE_u"):
    """
    Applies an imagefunction (eg. min, avg, max) to all images with the specified file_pre prefix
    and writes them to the database in a seperate row

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_function : function(db_path : string, image_path : string) =>
        tuple of n_components if n_components >= 1 else a value

            a function that takes 2 arguments, the path to a Cinema
        database and a relative path to an image. it returns a tuple
        of values with length equal to the number of components of the
        input image if n_components is None, otherwise it returns
        a tuple of values of length specified by n_components
        (or just a value if n_components is 0)

        prefix : prefix added to the name of the row before the image measure name

        csv_path : string = d.SPEC_D_CSV_FILENAME
            the relative POSIX path to data.csv (or otherwise named)

    side effects:
        writes the image metric functions results to the csv file
    """
    headerlist = get_headerlist_from_csv(os.path.join(db_path, csv_path))

    uncertainty_index_list = []
    for index, headertitle in enumerate(headerlist):
        if headertitle.startswith(file_pre):
            uncertainty_index_list.append([index, headertitle[len(file_pre):]])

    added_rows = 0
    for i in uncertainty_index_list:
        d_im_image.file_add_column(db_path, i[0] + added_rows, "u_" + prefix + i[1], imagefunction)
        added_rows += 1


def get_filenames_from_csv(path_to_csv, column_number):
    """
    Returns a list of all filenames of the given column
    if it is a FILE column

    arguments:
        path_to_csv : string
            POSIX path to the Cinema database csv file

        column_number : integer >= 0
            FILE column that contains the image files

    returns:
        a list of filenames
    """
    filenames = []
    with open(path_to_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = True
        for row in csv_reader:
            if header:
                header = False
                if not row[column_number].startswith("FILE"):
                    return []
            else:
                filenames.append(row[column_number])
    return filenames


def get_headerlist_from_csv(path_to_csv):
    """
    Returns a list of all header names in the csv file

    arguments:
        path_to_csv : string
            POSIX path to the Cinema database csv file

    returns:
        a list of header names
    """
    with open(path_to_csv) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        return next(reader, None)


def calculate_uncertainty_acutance(db_path, image_path, suffix="_u_acutance", file_ext="png"):
    """
    Calculated the acutance uncertainty measure

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_acutance"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database

    side effects:
        writes out the uncertainty image
    """
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if pw.image_exsists(os.path.join(db_path, new_fn)):
        print(new_fn, "already exsists!")
        return new_fn
    im = pw.open_image(os.path.join(db_path, image_path))
    acutance_error_im = ec.get_acutance_error(im)
    acutance_error_im.save(os.path.join(db_path, new_fn))
    print("Calculated", new_fn)

    return new_fn


def calculate_uncertainty_gaussian(db_path, image_path, suffix="_u_gaussian", file_ext="png"):
    """
    Calculated the gaussian uncertainty measure

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_gaussian"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database

    side effects:
        writes out the uncertainty image
    """
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if pw.image_exsists(os.path.join(db_path, new_fn)):
        print(new_fn, "already exsists!")
        return new_fn
    im = pw.open_image(os.path.join(db_path, image_path))
    gaussian_histogram = es.get_gaussian_noise_histogram(pw.convert_grayscale(im))
    gaussian_error_im = ec.get_gaussian_error(im, gaussian_histogram)
    gaussian_error_im.save(os.path.join(db_path, new_fn))
    print("Calculated", new_fn)

    return new_fn


def calculate_uncertainty_local_contrast(db_path, image_path, suffix="_u_local_contrast", file_ext="png"):
    """
    Calculated the local contrast uncertainty measure

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_local_contrast"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database

    side effects:
        writes out the uncertainty image
    """
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if pw.image_exsists(os.path.join(db_path, new_fn)):
        print(new_fn, "already exsists!")
        return new_fn
    im = pw.open_image(os.path.join(db_path, image_path))
    contrast_histogram = es.get_contrast_histogram(pw.convert_grayscale(im))
    local_contrast_error_im = ec.get_local_contrast_error(im, contrast_histogram)
    local_contrast_error_im.save(os.path.join(db_path, new_fn))
    print("Calculated", new_fn)

    return new_fn


def calculate_uncertainty_local_range(db_path, image_path, suffix="_u_local_range", file_ext="png"):
    """
    Calculated the local range uncertainty measure

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_local_range"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database

    side effects:
        writes out the uncertainty image
    """
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if pw.image_exsists(os.path.join(db_path, new_fn)):
        print(new_fn, "already exsists!")
        return new_fn
    im = pw.open_image(os.path.join(db_path, image_path))
    local_range_error_im = ec.get_local_range_error(im, 2)
    local_range_error_im.save(os.path.join(db_path, new_fn))
    print("Calculated", new_fn)

    return new_fn


def calculate_uncertainty_salt_and_pepper(db_path, image_path, suffix="_u_salt_and_pepper", file_ext="png"):
    """
    Calculated the salt and pepper uncertainty measure

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_salt_and_pepper"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database

    side effects:
        writes out the uncertainty image
    """
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if pw.image_exsists(os.path.join(db_path, new_fn)):
        print(new_fn, "already exsists!")
        return new_fn
    im = pw.open_image(os.path.join(db_path, image_path))
    salt_and_pepper_error_im = ec.get_salt_and_pepper_error(im, 2)
    salt_and_pepper_error_im.save(os.path.join(db_path, new_fn))
    print("Calculated", new_fn)

    return new_fn


def calculate_uncertainty_brightness(db_path, image_path, suffix="_u_brightness", file_ext="png"):
    """
    Calculated the brightness uncertainty measure

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_brightness"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database

    side effects:
        writes out the uncertainty image
    """
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if pw.image_exsists(os.path.join(db_path, new_fn)):
        print(new_fn, "already exsists!")
        return new_fn
    im = pw.open_image(os.path.join(db_path, image_path))
    brightness_error_im = ec.get_brightness_error(im)
    brightness_error_im.save(os.path.join(db_path, new_fn))
    print("Calculated", new_fn)

    return new_fn


def calculate_uncertainty_contrast_strech(db_path, image_path, suffix="_u_contrast_strech", file_ext="png"):
    """
    Calculated the contrast strech uncertainty measure

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_contrast_strech"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database

    side effects:
        writes out the uncertainty image
    """
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if pw.image_exsists(os.path.join(db_path, new_fn)):
        print(new_fn, "already exsists!")
        return new_fn
    im = pw.open_image(os.path.join(db_path, image_path))
    contrast_strech_error_im = ec.get_contrast_strech_error(im, 10.0, 90.0)
    contrast_strech_error_im.save(os.path.join(db_path, new_fn))
    print("Calculated", new_fn)

    return new_fn


"""
Create DB entries
"""


def create_db_entry_uncertainty_acutance(db_path, image_path, suffix="_u_acutance", file_ext="png"):
    """
    Creates the uncertainty image database entries

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_acutance"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database, if file exsits
        notFound, otherwise

    side effects:
        writes the relative POSIX image paths to the Cinema database
    """
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_gaussian(db_path, image_path, suffix="_u_gaussian", file_ext="png"):
    """
    Creates the gaussian uncertainty image database entries

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_gaussian"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database, if file exsits
        notFound, otherwise

    side effects:
        writes the relative POSIX image paths to the Cinema database
    """
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_local_contrast(db_path, image_path, suffix="_u_local_contrast", file_ext="png"):
    """
    Creates the local contrast uncertainty image database entries

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_local_contrast"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database, if file exsits
        notFound, otherwise

    side effects:
        writes the relative POSIX image paths to the Cinema database
    """
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_local_range(db_path, image_path, suffix="_u_local_range", file_ext="png"):
    """
    Creates the local range uncertainty image database entries

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_local_range"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database, if file exsits
        notFound, otherwise

    side effects:
        writes the relative POSIX image paths to the Cinema database
    """
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_salt_and_pepper(db_path, image_path, suffix="_u_salt_and_pepper", file_ext="png"):
    """
    Creates the salt and peper uncertainty image database entries

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_salt_and_pepper"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database, if file exsits
        notFound, otherwise

    side effects:
        writes the relative POSIX image paths to the Cinema database
    """
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_brightness(db_path, image_path, suffix="_u_brightness", file_ext="png"):
    """
    Creates the brightness uncertainty image database entries

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_brightness"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database, if file exsits
        notFound, otherwise

    side effects:
        writes the relative POSIX image paths to the Cinema database
    """
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_contrast_strech(db_path, image_path, suffix="_u_contrast_strech", file_ext="png"):
    """
    Creates the contrast strech uncertainty image database entries

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

        suffix : string = "_u_contrast_strech"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new uncertainty image as

    returns:
        the new relative POSIX path to the image from the Cinema database, if file exsits
        notFound, otherwise

    side effects:
        writes the relative POSIX image paths to the Cinema database
    """
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"
