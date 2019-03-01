from . import pillow_wrapper as pw
from . import error_calculation as ec
from . import error_statistics_calculation as es
from ..spec import d
import os


def calculate_uncertainty(db_path, column_number, csv_path="data.csv"):
    # get the first image
    data = d.get_iterator(db_path, csv_path)
    next(data)
    next(data)
    next(data)
    next(data)
    next(data)
    for row in data:
        if None is not row[column_number] != " ":
            impath = (os.path.join(db_path, row[column_number]))
            im = pw.open_image(impath)
            splitpath = os.path.split(impath)
            splitfile = os.path.splitext(splitpath[1])

            print(splitfile, "_acutance")
            acutance_error_im = ec.get_acutance_error(im)
            acutance_error_im.save(splitpath[0] + "/" + splitfile[0] + "_acutance" + splitfile[1])

            print(splitfile, "_gaussian")
            gaussian_histogram = es.get_gaussian_noise_histogram(pw.convert_grayscale(im))
            gaussian_error_im = ec.get_gaussian_error(im, gaussian_histogram)
            gaussian_error_im.save(splitpath[0] + "/" + splitfile[0] + "_gaussian" + splitfile[1])

            print(splitfile, "_contrast")
            contrast_histogram = es.get_contrast_histogram(pw.convert_grayscale(im))
            local_contrast_error_im = ec.get_local_contrast_error(im, contrast_histogram)
            local_contrast_error_im.save(splitpath[0] + "/" + splitfile[0] + "_contrast" + splitfile[1])

            print(splitfile, "_localrange")
            localrange_error_im = ec.get_local_range_error(im, 2)
            localrange_error_im.save(splitpath[0] + "/" + splitfile[0] + "_localrange" + splitfile[1])

            print(splitfile, "_saltandpepper")
            salt_and_pepper_error_im = ec.get_salt_and_pepper_error(im, 2)
            salt_and_pepper_error_im.save(splitpath[0] + "/" + splitfile[0] + "_saltandpepper" + splitfile[1])

            print(splitfile, "_brightness")
            brightness_error_im = ec.get_brightness_error(im)
            brightness_error_im.save(splitpath[0] + "/" + splitfile[0] + "_brightness" + splitfile[1])

            print(splitfile, "_contrast")
            contrast_strech_error_im = ec.get_contrast_strech_error(im, 10.0, 90.0)
            contrast_strech_error_im.save(splitpath[0] + "/" + splitfile[0] + "_contrast" + splitfile[1])

    # close the file
    del data
