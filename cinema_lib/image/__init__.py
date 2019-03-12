"""
Cinema utility functions for processing image data.
"""

from skimage import io
from skimage import color
from skimage import feature
import numpy as np
import os

from .. import check_numpy_version     
                    
try:               
    check_numpy_version(np)            
except Exception as e:                 
    raise e        


def file_mean(db_path, image_path):
    """
    Calculate the mean of an image file. For multi-component images,
    it returns the average vector (RGBA, etc.)

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

    returns:
        the minimum scalar or vector of the image
    """

    return np.mean(io.imread(os.path.join(db_path, image_path)), (0, 1))


def file_max(db_path, image_path):
    """
    Calculate the maximum of an image file. For multi-component images,
    it returns the average vector (RGBA, etc.)

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

    returns:
        the maximum scalar or vector of the image
    """

    return np.amax(io.imread(os.path.join(db_path, image_path)), (0, 1))


def file_min(db_path, image_path):
    """
    Calculate the minimum of an image file. For multi-component images,
    it returns the average vector (RGBA, etc.)

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

    returns:
        the average scalar or vector of the image
    """
    return np.amin(io.imread(os.path.join(db_path, image_path)), (0, 1))


def file_grey(db_path, image_path, suffix="_image_grey", file_ext="png"):
    """
    Generate the greyscale of an image file. Uses Scikit-image color
    rgb2grey for the conversion. Requires that the input image is RGB.

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_image_grey"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new greyscale image as

    returns:
        the relative path of the new greyscale image

    side effects:
        writes out the greyscale image 
    """

    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext 
    io.imsave(os.path.join(db_path, new_fn), 
              color.rgb2grey(io.imread(os.path.join(db_path, image_path))))

    return new_fn


def file_stddev(db_path, image_path):
    """
    Calculate the standard deviation of an image file. For multi-component 
    images, it returns the standard deviation of the vector components
    (RGBA, etc.)

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to the image from the Cinema database

    returns:
        the standard deviation scalar or per-component of vector of the image
    """

    return np.std(io.imread(os.path.join(db_path, image_path)), (0, 1))


def __entropy(im, bins):
    histogram = np.histogram(im, bins)[0]
    histogram = histogram / float(np.sum(histogram))
    return -np.sum(histogram * np.log2(histogram, where=histogram > 0)) 


def file_shannon_entropy(db_path, image_path, bins=131072):
    """
    Calculate the Shannon entropy of an image file. For multi-component 
    images, it returns the entropy of the vector components (RGBA, etc.)

    arguments:
        db_path : string
            POSIX path for the Cinema database
        image_path : string
            relative POSIX path to the image from the Cinema database
        bins : integer = 131072 (or whatever numpy.histogram takes)
            the number of bins to use to calculate the histogram 
            (probabilities) -- see numpy.histogram for more options
            on bins arguments

    returns:
        the entropy scalar or per-component of entropy of the image
    """

    im = io.imread(os.path.join(db_path, image_path))
    if len(im.shape) == 2:
        return __entropy(im, bins)
    else:
        return [__entropy(im[:,:,d], bins) for d in range(0, im.shape[2])]


def file_unique_count(db_path, image_path):
    """
    Calculate a count of the number of unique pixels in an image file.

    arguments:
        db_path : string
            POSIX path for the Cinema database
        image_path : string
            relative POSIX path to the image from the Cinema database

    returns:
        the count of the unique pixels in the image
    """
   
    im = io.imread(os.path.join(db_path, image_path))
    if len(im.shape) == 2:
        return len(np.unique(im))
    else:
        s = im.shape
        return len(np.unique(im.reshape(s[0]*s[1], s[2]), axis=0))


def file_canny_count(db_path, image_path):
    """
    Calculate a count of the number of edge pixels using the Canny edge 
    detector.  For multi-component images, it returns the pixel edge
    count for each of the vector components (RGBA, etc.)

    arguments:
        db_path : string
            POSIX path for the Cinema database
        image_path : string
            relative POSIX path to the image from the Cinema database.

    returns:
        the count of the number of Canny edge pixels in the image
    """

    im = io.imread(os.path.join(db_path, image_path))
    if len(im.shape) == 2:
        return np.sum(feature.canny(im))
    else:
        return \
            [np.sum(feature.canny(im[:,:,d])) for d in range(0, im.shape[2])]


def file_percentile(db_path, image_path, percent):
    """
    Calculate the percentile value of the image at percent. For multi-component
    images, it returns the percentile value for each of the vector
    components (RGBA, etc.)

    arguments:
        db_path : string
            posix path for the cinema database
        image_path : string
            relative posix path to the image from the cinema database.
        percentile : float
            percentile between [0, 100] to compute

    returns:
        returns the value of the percentile
    """

    im = io.imread(os.path.join(db_path, image_path))

    if len(im.shape) == 2:
        return np.percentile(im, percent, interpolation='nearest')
    else:
        return [np.percentile(im[:,:,d], percent, interpolation='nearest') for
                d in range(0, im.shape[2])]


def file_joint_entropy(db_path, image_path, discretization=1024):
    """
    Calculate the joint entropy (entropy of the joint probability of 
    multi-component images). If the image is single component (scalar), 
    it returns the same as file_shannon_entropy.

    arguments:
        db_path : string
            posix path for the cinema database
        image_path : string
            relative posix path to the image from the cinema database.
        discretization : integer = 1024
            how many discretization levels to use per component (dimension)

    returns:
        the joint entropy of the image
    """

    im = io.imread(os.path.join(db_path, image_path))
    if len(im.shape) == 2:
        return file_shannon_entropy(db_path, image_path, discretization)
    else:
        total = im.shape[0] * im.shape[1] 
        im = im.reshape(total, im.shape[2])
        mins = np.amin(im, 0)
        maxs = np.amax(im, 0)
        scale = discretization / (maxs - mins)
        im = np.clip(np.floor((im - mins) * scale), 
                a_min=np.array((0,)*im.shape[1]),
                a_max=np.array((discretization-1,)*im.shape[1]))
        u, u_counts = np.unique(im, return_counts=True, axis=0)
        u_counts = u_counts.astype(np.float64) / total
        return -np.sum(u_counts * np.log2(u_counts)) 
