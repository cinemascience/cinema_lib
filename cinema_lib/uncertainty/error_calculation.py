from . import pillow_wrapper as pw
from . import error_statistics_calculation as es
import math
import sys


# Create a Grayscale version of the image
def get_acutance_error(image):
    """
    Calculates the acutance error of an image.
    Acutance describes the probability of an voxel to lie on an edge
    in an image. The longer the derivate in a pixel is the more likely
    this pixel is located on an edge and therefore the uncertainty is low.

    arguments:
        image : Pillow image object
            original image

    returns:
        a greyscale image providing the uncertainty information
        for the acutance error
    """
    # Get size
    width, height = image.size

    # number of color channels
    channel_count = len(image.getbands())

    # Create new Image and a Pixel Map
    acutancepicture = pw.create_image_greyscale(width, height)
    pixels = acutancepicture.load()

    pixellength = math.sqrt(255.0 ** 2 + 255.0 ** 2)

    for y in range(height):
        for x in range(width):
            result = 0.0
            for channel in range(channel_count):
                acutancexm = 0.0
                acutancexp = 0.0
                acutanceym = 0.0
                acutanceyp = 0.0

                if x - 1 >= 0:
                    acutancexm = abs(pw.get_pixel(image, x, y)[channel] - pw.get_pixel(image, x - 1, y)[channel])

                if x + 1 < width:
                    acutancexp = abs(pw.get_pixel(image, x, y)[channel] - pw.get_pixel(image, x + 1, y)[channel])

                if y - 1 >= 0:
                    acutanceym = abs(pw.get_pixel(image, x, y)[channel] - pw.get_pixel(image, x, y - 1)[channel])

                if y + 1 < height:
                    acutanceyp = abs(pw.get_pixel(image, x, y)[channel] - pw.get_pixel(image, x, y + 1)[channel])

                acutancelengthm = math.sqrt(acutancexm ** 2 + acutanceym ** 2) / pixellength
                acutancelengthp = math.sqrt(acutancexp ** 2 + acutanceyp ** 2) / pixellength

                result += pow(acutancelengthm, 2)
                result += pow(acutancelengthp, 2)

            result = math.sqrt(1 - (result / (channel_count * 2))) * 255.0

            # set pixel in new image
            pixels[x, y] = (int(result))

    # return new image
    return acutancepicture


def get_gaussian_error(image, gauss_histogram):
    """
    Calculates the gaussian error of an image.
    The gaussian error assumes a gaussian distribution of signal values.
    Each pixel gets the coresponding value of their intensity in the gaussian
    histogram.

    arguments:
        image : Pillow image object
            original image

        gauss_histogram : array
            normalized histogram of the gaussian distribution for each intensity value

    returns:
        a greyscale image providing the uncertainty information
        for the gaussian error
    """
    # get size
    width, height = image.size

    # number of color channels
    channel_count = len(image.getbands())

    # create new image and a pixel map
    gaussian_error_picture = pw.create_image_greyscale(width, height)
    pixels = gaussian_error_picture.load()

    for y in range(height):
        for x in range(width):
            result = 0.0

            for color_channel in range(channel_count):
                value = int(math.floor(pw.get_pixel(image, x, y)[color_channel]))
                result += math.pow(gauss_histogram[value], 2)

            result = (result / channel_count) * 255.0

            # Set Pixel in new image
            pixels[x, y] = (int(result))

    return gaussian_error_picture


def get_local_contrast_error(image, contrast_histogram):
    """
    Calculates the local contrast error of an image.
    Often used intensity values are considered to be more trustworthy.

    arguments:
        image : Pillow image object
            original image

        contrast_histogram : array
            normalized histogram of the intensity value distribution

    returns:
        a greyscale image providing the uncertainty information
        for the local contrast error
    """
    # Get size
    width, height = image.size

    # number of color channels
    channel_count = len(image.getbands())

    # Create new Image and a Pixel Map
    local_contrast_error_picture = pw.create_image_greyscale(width, height)
    pixels = local_contrast_error_picture.load()

    for y in range(height):
        for x in range(width):
            result = 0.0

            for color_channel in range(channel_count):
                value = int(math.floor(pw.get_pixel(image, x, y)[color_channel]))
                result += math.pow(contrast_histogram[value], 2)

            result = (result / channel_count) * 255.0

            # Set Pixel in new image
            pixels[x, y] = (int(result))

    return local_contrast_error_picture


def get_local_range_error(image, neighborhood_radius):
    """
    Calculates the local range error of an image.
    Considers homogenous regions as certain.
    Each pixels neighborhood gets checked for their max
    and min intensity value.
    The difference of those values is the result.

    arguments:
        image : Pillow image object
            original image

        neighborhood_radius : integer
            radius for the neighborhood search

    returns:
        a greyscale image providing the uncertainty information
        for the local range error
    """
    if neighborhood_radius < 1:
        return pw.create_image(1, 1)

    # Get size
    width, height = image.size

    # number of color channels
    channel_count = len(image.getbands())

    # Create new Image and a Pixel Map
    local_range_error_picture = pw.create_image_greyscale(width, height)
    pixels = local_range_error_picture.load()

    # iterate over all pixels and channels
    for y in range(height):
        for x in range(width):
            local_range_of_all_components = 0.0

            for color_channel in range(channel_count):
                max_value = float('-inf')
                min_value = float('inf')

                local_range = 0.0

                # calculate the maximum and minimum value for the neighborhood
                for localy in range(-neighborhood_radius, neighborhood_radius + 1):
                    for localx in range(-neighborhood_radius, neighborhood_radius + 1):

                        newx = 0
                        newy = 0

                        if 0 <= (x + localx) < width and 0 <= (y + localy) < height:
                            newx = x + localx
                            newy = y + localy

                            local_value = pw.get_pixel(image, newx, newy)[color_channel]

                            if max_value < local_value:
                                max_value = local_value

                            if min_value > local_value:
                                min_value = local_value

                # scale to 0-1 range
                local_range = (max_value - min_value) / 255.0
                local_range_of_all_components += local_range ** 2

            # reverse pow and map to pixel values
            local_range_of_all_components = math.sqrt(local_range_of_all_components / channel_count) * 255.0

            # Set Pixel in new image
            pixels[x, y] = (int(local_range_of_all_components))

    return local_range_error_picture


def get_salt_and_pepper_error(image, neighborhood_radius):
    """
    Calculates the salt and pepper error of an image.
    Considers homogenous regions as certain.
    Takes the average of all intensities in the neighborhood.
    The difference of this value and the pixel intensity is the result.

    arguments:
        image : Pillow image object
            original image

        neighborhood_radius : integer
            radius for the neighborhood search

    returns:
        a greyscale image providing the uncertainty information
        for the salt and pepper error
    """
    if neighborhood_radius < 1:
        return pw.create_image(1, 1)

    # Get size
    width, height = image.size

    # number of color channels
    channel_count = len(image.getbands())

    # Create new Image and a Pixel Map
    get_salt_and_pepper_error_picture = pw.create_image_greyscale(width, height)
    pixels = get_salt_and_pepper_error_picture.load()

    # iterate over all pixels and channels
    for y in range(height):
        for x in range(width):
            salt_and_pepper = 0.0

            for color_channel in range(channel_count):
                sum_of_neighbors = 0.0
                neighborhood_avg = 0.0
                number_of_pixels = 0

                # calculate the average value for the neighborhood
                for localy in range(-neighborhood_radius, neighborhood_radius + 1):
                    for localx in range(-neighborhood_radius, neighborhood_radius + 1):

                        newx = 0
                        newy = 0

                        if 0 <= (x + localx) < width and 0 <= (y + localy) < height:
                            newx = x + localx
                            newy = y + localy

                            local_value = pw.get_pixel(image, newx, newy)[color_channel]

                            sum_of_neighbors += local_value
                            number_of_pixels += 1

                neighborhood_avg = sum_of_neighbors / number_of_pixels

                difference = abs(neighborhood_avg - pw.get_pixel(image, x, y)[color_channel]) / 255.0

                salt_and_pepper += difference ** 2

            salt_and_pepper = math.sqrt(salt_and_pepper / channel_count) * 255.0

            # Set Pixel in new image
            pixels[x, y] = (int(salt_and_pepper))

    return get_salt_and_pepper_error_picture


def get_brightness_error(image):
    """
    Calculates the brightness error of an image.
    This measure interprets bright pixels as certaint and
    dark pixels as uncertain.
    Therefor this outputs an inverse of the given picture


    arguments:
        image : Pillow image object
            original image

    returns:
        a greyscale image providing the uncertainty information
        for the brightness error
    """
    # Get size
    width, height = image.size

    # number of color channels
    channel_count = len(image.getbands())

    # Create new Image and a Pixel Map
    brightness_error_picture = pw.create_image_greyscale(width, height)
    pixels = brightness_error_picture.load()

    # iterate over all pixels and channels
    for y in range(height):
        for x in range(width):
            brightness = 0.0

            for color_channel in range(channel_count):
                brightness += pw.get_pixel(image, x, y)[color_channel] / 255.0

            brightness = (1 - (brightness / channel_count)) * 255.0

            # Set Pixel in new image
            pixels[x, y] = (int(brightness))

    return brightness_error_picture


def get_contrast_strech_error(image, min_percentage, max_percentage):
    """
    Calculates the contrast strech error of an image.
    This measure estimates how close the current histogram is to a
    streched histogram.
    For better results a percentage of the intesity values can be
    ignored.
    if the value in the new histogram does not change hat all the
    pixel is considered very certain.


    arguments:
        image : Pillow image object
            original image
        min_percentage:
            percentage of low pixel intensities to ignore
        max_percentage:
            percentage of high pixel intensities to ignore

    returns:
        a greyscale image providing the uncertainty information
        for the contrast streh error
    """
    # Get size
    width, height = image.size

    # number of color channels
    channel_count = len(image.getbands())

    grayscale_image = pw.convert_grayscale(image)
    contrast_strech_picture = None
    histograms = []

    if channel_count > 1:
        contrast_strech_picture = pw.create_image(width, height)
        multi_bands = image.split()
        for i in range(len(multi_bands)):
            histograms.append(es.get_percentage_histogram(multi_bands[i]))
    else:
        contrast_strech_picture = pw.create_image_greyscale(width, height)
        histograms = [es.get_percentage_histogram(image)]

    pixels = contrast_strech_picture.load()

    for y in range(height):
        for x in range(width):
            intensities = []
            for color_channel in range(channel_count):
                min_value = es.get_intensity_at_percentage(histograms[color_channel], min_percentage)
                max_value = es.get_intensity_at_percentage(histograms[color_channel], max_percentage)
                intensities.append(
                    es.normalize_intensity(pw.get_pixel(image, x, y)[color_channel], min_value, max_value))

            # Set Pixel in new image
            if channel_count > 1:
                pixels[x, y] = (int(intensities[0]), int(intensities[1]), int(intensities[2]))
            else:
                pixels[x, y] = (int(intensities[0]))

    if channel_count > 1:
        return pw.get_diff_image(pw.convert_grayscale(contrast_strech_picture), grayscale_image).split()[0]
    else:
        return pw.get_diff_image(contrast_strech_picture, grayscale_image.split()[0])
