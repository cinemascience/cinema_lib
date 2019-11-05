"""
Cinema utility functions for processing image data using OpenCV.
"""

import cv2
import os
import numpy as np

from .. import check_numpy_version     
                    
try:               
    check_numpy_version(np)            
except Exception as e:                 
    raise e        

def file_grey(db_path, image_path, suffix="_cv_grey", file_ext="png"):
    """
    Generate the greyscale of an image file. Uses opencv cvtColor
    for the conversion. 

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_grey"
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
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(os.path.join(db_path, new_fn), grey)
    
    return new_fn

def file_box_blur(db_path, image_path, suffix="_cv_box_blur", file_ext="png",
        size=10):

    """
    Generate a box blurred image file. Uses opencv blur for the conversion. 

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_box_blur"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new image as

        size : integer, default = 10
            size of the box filter

    returns:
        the relative path of the new blurred image

    side effects:
        writes out the blurred image 
    """

    new_fn = os.path.splitext(image_path)[0] + suffix + "_" + str(size) + "." + file_ext
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    blur = cv2.blur(img, (size, size))
    cv2.imwrite(os.path.join(db_path, new_fn), blur)

    return new_fn

def file_gaussian_blur(db_path, image_path, suffix="_cv_gaussian_blur", 
        file_ext="png", size=11):
    """
    Generate a Gaussian blurred image file. Uses opencv GaussianBlur
    for the conversion. 

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_gaussian_blur"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new image as

        size : odd integer; default = 11
            size of the Gaussian filter, odd integers
            if the user input size is even, add one to make it odd
                                                    
    returns:
        the relative path of the new blurred image

    side effects:
        writes out the blurred image 
    """
    if (size % 2 == 0):
        size = size + 1

    new_fn = os.path.splitext(image_path)[0] + suffix + "_" + str(size) + "." + file_ext
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    blur = cv2.GaussianBlur(img, (size, size), 0)
    cv2.imwrite(os.path.join(db_path, new_fn), blur)
    
    return new_fn

def file_median_blur(db_path, image_path, suffix="_cv_median_blur", 
        file_ext="png", size=11):
    """
    Generate a median blurred image file. Uses opencv medianBlur for the 
    conversion. 

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_median_blur"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new image as

        size : odd integer; default = 11
            size of the median filter, odd integers
            if the user input size is even, add one to make it odd

    returns:
        the relative path of the new blurred image

    side effects:
        writes out the blurred image 
    """
    if (size % 2 == 0):
        size = size + 1

    new_fn = os.path.splitext(image_path)[0] + suffix + "_" + str(size) + "." + file_ext
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    blur = cv2.medianBlur(img, size)
    cv2.imwrite(os.path.join(db_path, new_fn), blur)
    
    return new_fn

def file_bilateral_filter(db_path, image_path, suffix="_cv_bilateral_filter", 
        file_ext="png", diameter=5, sigma_color=150, sigma_space=150):
    """
    Generate an image file using bilateral filter. Uses opencv bilateralFilter 
    for the conversion. 

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_bilateral_filter"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new image as

        diameter : integer; default = 5 
            diameter of the pixel neighborhood. diameter is calculated from
            sigma_space if <= 0

        sigma_color : integer = 150
            delta in color space that is considered to be similar colors

        sigma_space : integer = 150
            delta in image space that is considered for similar pixels.
            diameter is calculated from this if it is <= 0

    returns:
        the relative path of the new filtered image

    side effects:
        writes out the filtered image 
    """

    new_fn = os.path.splitext(image_path)[0] + suffix + "_" + str(diameter) + "." + file_ext
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    blur = cv2.bilateralFilter(img, diameter, sigma_color, sigma_space)
    cv2.imwrite(os.path.join(db_path, new_fn), blur)
    
    return new_fn

def file_canny(db_path, image_path, suffix="_cv_canny", file_ext="png",
        lower_threshold=100, upper_threshold=200, sobel_size=3, 
        l2_gradient=False):
    """
    Generate an image file using Canny edge detector. Uses opencv Canny 
    for the conversion. 

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_canny"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new image as

        lower_threshold : integer; default = 100
            the lower threshold that a pixel is considered an edge, if
            it is connected to a pixel that has passed the upper threshold

        upper_threshold : integer; default = 200
            the threshold that a pixel is definitively considered an edge
            must be larger than the lower_threshold

        sobel_size : integer that is 1, 3, 5, or 7 = 3
            size of the Sobel operator (gradient detector)

        l2_gradient : boolean = False
            use the L2 norm instead of the L1 norm for gradient calculations

    returns:
        the relative path of the new filtered image

    side effects:
        writes out the filtered image 
    """

    if (upper_threshold <= lower_threshold):
        upper_threshold = lower_threshold + 1

    new_fn = os.path.splitext(image_path)[0] + suffix + "_" + str(lower_threshold) + "_" + str(upper_threshold) + "." + file_ext
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    edges = cv2.Canny(img, lower_threshold, upper_threshold, 
            apertureSize=sobel_size, L2gradient=l2_gradient)
    cv2.imwrite(os.path.join(db_path, new_fn), edges)
    
    return new_fn

def file_contour_threshold(db_path, image_path, suffix="_cv_contour_threshold", 
        file_ext="png", threshold=20, color=None, thickness=2):
    """
    Draws contours of a greyscale thresholded image on top of the 
    input image. Uses opencv threshold, findContours, and drawContours.

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_contour_threshold"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        file_ext : string = "png"
            the image file extension (MIME) to save the new image as

        threshold  : integer; default = 20 
            the greyscale threshold for creating the binary image
            value = [0,255]

        color : None or (integer, integer, integer) = None
            if None, will use the negative of the original image to
            draw the contours, otherwise will use the color
            (R, G, B) triple provided

        thickness : integer = 2
            thickness of the contours, negative integers result in filled
            contours

    returns:
        the relative path of the new image

    side effects:
        writes out the new image 
    """
    if (threshold < 0):
        threshold = 0
    if (threshold > 255):
        threshold = 255     
 
    new_fn = os.path.splitext(image_path)[0] + suffix + "_" + str(threshold) + "." + file_ext
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    otsu, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    mask, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE,
       cv2.CHAIN_APPROX_SIMPLE)
    if color == None:
        mask = cv2.drawContours(np.zeros(mask.shape), contours, -1, 255,
                thickness)
        cv2.imwrite(os.path.join(db_path, new_fn), np.where(
            mask[:,:,np.newaxis] > 0, 255 - img, img))
    else:
        img = cv2.drawContours(img, contours, -1,
                (color[2], color[1], color[0]), thickness)
        cv2.imwrite(os.path.join(db_path, new_fn), img)

    return new_fn

def file_fast_draw(db_path, image_path, suffix="_cv_fast_draw", file_ext="png",
        threshold=10, nonmax_suppression=True, 
        fast_type=cv2.FAST_FEATURE_DETECTOR_TYPE_9_16, color=None):
    """
    Draws FAST features of a greyscale image on top of the input image. Uses 
    opencv xfeatures2d FAST_create, detect, and drawKeypoints.

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_sift_draw"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        threshold : integer = 10
            intensity threshold difference for FAST calculation

        nonmax_suppression : boolean = True
            whether or not to use the non-maximal suppression technique
            in FAST

        fast_type : cv2 fast types = cv2.FAST_FEATURE_DETECTOR_TYPE_9_16
            type of FAST detector to use

        color : None or (integer, integer, integer) = None
            if None, will use the negative of the original image to
            draw the contours, otherwise will use the color
            (R, G, B) triple provided

    returns:
        the relative path of the new image

    side effects:
        writes out the new image 
    """

    new_fn = os.path.splitext(image_path)[0] + suffix + "." + file_ext
    img = cv2.imread(os.path.join(db_path, image_path), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fast = cv2.FastFeatureDetector_create(threshold, nonmax_suppression,
            fast_type)
    kp = fast.detect(gray, None)
    if color == None:
        mask = cv2.drawKeypoints(np.zeros(img.shape, img.dtype), kp, None, 255,
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imwrite(os.path.join(db_path, new_fn), np.where(
            mask > 0, 255 - img, img))
    else:
        img = cv2.drawKeypoints(img, kp, None, (color[2], color[1], color[0]),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        cv2.imwrite(os.path.join(db_path, new_fn), img)

    return new_fn

