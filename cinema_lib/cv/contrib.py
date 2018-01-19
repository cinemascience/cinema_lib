"""
Cinema utility functions for processing image data using OpenCV contrib.
"""

import cv2
import os
import numpy as np

from .. import check_numpy_version     
                    
try:               
    check_numpy_version(np)            
except Exception as e:                 
    raise e        

try:
    from cv2.xfeatures2d import SIFT_create
    from cv2.xfeatures2d import SURF_create
    from cv2 import FastFeatureDetector_create
except Exception as e:
    raise e

def file_sift_draw(db_path, image_path, suffix="_cv_sift_draw", file_ext="png",
        n_features=0, n_octave_layers=3, contrast_threshold=0.04, 
        edge_threshold=10, sigma=1.6, color=None):
    """
    Draws SIFT features of a greyscale image on top of the input image. Uses 
    opencv xfeatures2d SIFT_create, detect, and drawKeypoints.

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_sift_draw"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        n_features : integer = 0
            draws the top N SIFT features, if 0 draws all features

        n_octave_layers : integer = 3
            how many layers to use for DoG (Difference of Gaussian) octaves.
            (number of octaves is computed from the image)

        contrast_threshold : float = 0.04
            larger numbers filter out weak features 

        edge_threshold : float = 10
            smaller numbers filter out weak features

        sigma : float = 1.6 (approximately sqrt(2))
            one standard deviation of the level 0 octave Gaussian (larger 
            means more blurring)

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
    sift = cv2.xfeatures2d.SIFT_create(n_features, n_octave_layers,
            contrast_threshold, edge_threshold, sigma)
    kp = sift.detect(gray, None)
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

def file_surf_draw(db_path, image_path, suffix="_cv_surf_draw", file_ext="png",
        hessian_threshold=400, n_octaves=4, n_octave_layers=3, 
        use_128_descriptors=False, no_orientation=False, color=None):
    """
    Draws SURF features of a greyscale image on top of the input image. Uses 
    opencv xfeatures2d SURF_create, detect, and drawKeypoints.

    arguments:
        db_path : string
            POSIX path for the Cinema database

        image_path : string
            relative POSIX path to an RGB image from the Cinema database

        suffix : string = "_cv_sift_draw"
            a suffix string that is added to the original relative image
            path filename - WARNING: DO NOT MAKE IT "" (EMPTY STRING) OR
            YOU WILL POTENTIALLY OVERWRITE YOUR SOURCE IMAGES

        hessian_threshold : float = 400
            threshold for the Hessian detector in SURF

        n_octaves : integer = 4
            number of octaves to use in SURF

        n_octave_layers : integer = 3
            number of layers to use per octave

        use_128_descriptors : boolean = False
            use 128 length vector features instead of 64

        no_orientation : boolean = False
            do not calculate feature orientation 

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
    surf = cv2.xfeatures2d.SURF_create(hessian_threshold,
            n_octaves, n_octave_layers,
            use_128_descriptors, no_orientation)
    kp = surf.detect(gray, None)
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


