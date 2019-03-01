import pillow_wrapper as pw
import error_calculation as ec
import error_statistics_calculation as es
import sys
import os



file_list = os.listdir(sys.argv[1])

testimg = pw.open_image("testimage.jpg")
#testimggray = pw.convert_grayscale(testimg).split()[0]
#testimg = testimggray

#pw.save_image(ec.get_contrast_strech_error(testimg.split()[0], 10.0, 90.0), "/Users/maack/Documents/test.png")

testgrayimg = ec.get_acutance_error(testimg)
testgrayimg.show()

gaussian_histogram = es.get_gaussian_noise_histogram(pw.convert_grayscale(testimg))
gaussian_error_img = ec.get_gaussian_error(testimg, gaussian_histogram)
gaussian_error_img.show()

contrast_histogram = es.get_contrast_histogram(pw.convert_grayscale(testimg))
local_contrast_error_img = ec.get_local_contrast_error(testimg, contrast_histogram)
local_contrast_error_img.show()

localrange_error_img = ec.get_local_range_error(testimg, 2)
localrange_error_img.show()

salt_and_pepper_error_img = ec.get_salt_and_pepper_error(testimg, 2)
salt_and_pepper_error_img.show()

brightness_error_img = ec.get_brightness_error(testimg)
brightness_error_img.show()

contrast_strech_error_img = ec.get_contrast_strech_error(testimg, 10.0, 90.0)
contrast_strech_error_img.show()

