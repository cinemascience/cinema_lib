from . import pillow_wrapper as pw
from . import error_calculation as ec
from . import error_statistics_calculation as es
from .. import image
from ..image import d as d_im_image
from ..cv import d as d_cv_image
import csv
import os
from concurrent.futures import ProcessPoolExecutor


def calculate_uncertainty(db_path, column_number, csv_path="data.csv"):
    filenamelist = get_filenames_from_csv(os.path.join(db_path, csv_path), column_number)
    with ProcessPoolExecutor(max_workers=8) as executor:
        for i in filenamelist:
            try:
                pw.open_image(os.path.join(db_path, i))
            except IOError:
                print(os.path.join(db_path, i), "not found")
                continue
            #executor.submit(calculate_uncertainty_acutance, db_path, i)
            #executor.submit(calculate_uncertainty_gaussian, db_path, i)
            #executor.submit(calculate_uncertainty_local_contrast, db_path, i)
            #executor.submit(calculate_uncertainty_local_range, db_path, i)
            #executor.submit(calculate_uncertainty_salt_and_pepper, db_path, i)
            #executor.submit(calculate_uncertainty_brightness, db_path, i)
            executor.submit(calculate_uncertainty_contrast_strech, db_path, i)

    d_cv_image.file_add_file_column(db_path, column_number, "FILE_acutance", create_db_entry_uncertainty_acutance)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_gaussian", create_db_entry_uncertainty_gaussian)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_local_contrast",
                                    create_db_entry_uncertainty_local_contrast)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_local_range", create_db_entry_uncertainty_local_range)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_salt_and_pepper",
                                    create_db_entry_uncertainty_salt_and_pepper)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_brightness", create_db_entry_uncertainty_brightness)
    d_cv_image.file_add_file_column(db_path, column_number, "FILE_contrast_strech",
                                    create_db_entry_uncertainty_contrast_strech)

    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_min_acutance", image.file_min)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_avg_acutance", image.file_mean)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_max_acutance", image.file_max)
    column_number += 2

    d_im_image.file_add_column(db_path, column_number, "u_min_gaussian", image.file_min)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_avg_gaussian", image.file_mean)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_max_gaussian", image.file_max)
    column_number += 2

    d_im_image.file_add_column(db_path, column_number, "u_min_local_contrast", image.file_min)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_avg_local_contrast", image.file_mean)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_max_local_contrast", image.file_max)
    column_number += 2

    d_im_image.file_add_column(db_path, column_number, "u_min_local_range", image.file_min)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_avg_local_range", image.file_mean)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_max_local_range", image.file_max)
    column_number += 2

    d_im_image.file_add_column(db_path, column_number, "u_min_salt_and_pepper", image.file_min)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_avg_salt_and_pepper", image.file_mean)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_max_salt_and_pepper", image.file_max)
    column_number += 2

    d_im_image.file_add_column(db_path, column_number, "u_min_brightness", image.file_min)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_avg_brightness", image.file_mean)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_max_brightness", image.file_max)
    column_number += 2

    d_im_image.file_add_column(db_path, column_number, "u_min_contrast_strech", image.file_min)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_avg_contrast_strech", image.file_mean)
    column_number += 1
    d_im_image.file_add_column(db_path, column_number, "u_max_contrast_strech", image.file_max)


def get_filenames_from_csv(path_to_csv, coloumn):
    filenames = []
    with open(path_to_csv) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = True
        for row in csv_reader:
            if header:
                header = False
            else:
                filenames.append(row[coloumn])
    return filenames


def calculate_uncertainty_acutance(db_path, image_path, suffix="_acutance", file_ext="png"):
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print("Calculating", new_fn)
    im = pw.open_image(os.path.join(db_path, image_path))
    acutance_error_im = ec.get_acutance_error(im)
    acutance_error_im.save(os.path.join(db_path, new_fn))

    return new_fn


def calculate_uncertainty_gaussian(db_path, image_path, suffix="_gaussian", file_ext="png"):
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print("Calculating", new_fn)
    im = pw.open_image(os.path.join(db_path, image_path))
    gaussian_histogram = es.get_gaussian_noise_histogram(pw.convert_grayscale(im))
    gaussian_error_im = ec.get_gaussian_error(im, gaussian_histogram)
    gaussian_error_im.save(os.path.join(db_path, new_fn))

    return new_fn


def calculate_uncertainty_local_contrast(db_path, image_path, suffix="_local_contrast", file_ext="png"):
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print("Calculating", new_fn)
    im = pw.open_image(os.path.join(db_path, image_path))
    contrast_histogram = es.get_contrast_histogram(pw.convert_grayscale(im))
    local_contrast_error_im = ec.get_local_contrast_error(im, contrast_histogram)
    local_contrast_error_im.save(os.path.join(db_path, new_fn))

    return new_fn


def calculate_uncertainty_local_range(db_path, image_path, suffix="_local_range", file_ext="png"):
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print("Calculating", new_fn)
    im = pw.open_image(os.path.join(db_path, image_path))
    local_range_error_im = ec.get_local_range_error(im, 2)
    local_range_error_im.save(os.path.join(db_path, new_fn))

    return new_fn


def calculate_uncertainty_salt_and_pepper(db_path, image_path, suffix="_salt_and_pepper", file_ext="png"):
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print("Calculating", new_fn)
    im = pw.open_image(os.path.join(db_path, image_path))
    salt_and_pepper_error_im = ec.get_salt_and_pepper_error(im, 2)
    salt_and_pepper_error_im.save(os.path.join(db_path, new_fn))

    return new_fn


def calculate_uncertainty_brightness(db_path, image_path, suffix="_brightness", file_ext="png"):
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print("Calculating", new_fn)
    im = pw.open_image(os.path.join(db_path, image_path))
    brightness_error_im = ec.get_brightness_error(im)
    brightness_error_im.save(os.path.join(db_path, new_fn))

    return new_fn


def calculate_uncertainty_contrast_strech(db_path, image_path, suffix="_contrast_strech", file_ext="png"):
    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print("Calculating", new_fn)
    im = pw.open_image(os.path.join(db_path, image_path))
    contrast_strech_error_im = ec.get_contrast_strech_error(im, 10.0, 90.0)
    contrast_strech_error_im.save(os.path.join(db_path, new_fn))

    return new_fn


"""
Create DB entries
"""


def create_db_entry_uncertainty_acutance(db_path, image_path, suffix="_acutance", file_ext="png"):
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    print(db_path, path, os.path.isfile(os.path.join(db_path, path)))
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_gaussian(db_path, image_path, suffix="_gaussian", file_ext="png"):
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_local_contrast(db_path, image_path, suffix="_local_contrast", file_ext="png"):
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_local_range(db_path, image_path, suffix="_local_range", file_ext="png"):
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_salt_and_pepper(db_path, image_path, suffix="_salt_and_pepper", file_ext="png"):
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_brightness(db_path, image_path, suffix="_brightness", file_ext="png"):
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"


def create_db_entry_uncertainty_contrast_strech(db_path, image_path, suffix="_contrast_strech", file_ext="png"):
    path = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    if os.path.isfile(os.path.join(db_path, path)):
        return path
    else:
        return "notFound"
