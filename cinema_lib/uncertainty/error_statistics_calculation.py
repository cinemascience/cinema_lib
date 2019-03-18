from . import pillow_wrapper as pw
from . import error_statistics_calculation as es
import math


def get_mean(grayscale_image):
	# Get size
	width, height = grayscale_image.size

	sum = 0.0
	for x in range(width):
		for y in range(height):
			sum += pw.get_pixel(grayscale_image, x, y)[0]

	return sum / (width * height)


def get_stadard_deviation(grayscale_image, mean):
	# Get size
	width, height = grayscale_image.size

	sum = 0.0
	for x in range(width):
		for y in range(height):
			sum += pow(pw.get_pixel(grayscale_image, x, y)[0] - mean, 2)

	return sum / (width * height)


def get_gaussian_noise_histogram(grayscale_image):
	width, height = grayscale_image.size

	mean = get_mean(grayscale_image)
	stadard_deviation = get_stadard_deviation(grayscale_image, mean)

	max_value = float('-inf')
	min_value = float('inf')

	# calculate total error
	histogram = [0.0] * 256
	for i in range(256):
		basis = math.sqrt((1 / 2 * 3.1415 * stadard_deviation) * math.exp(1))
		exponent = -((i - mean) / (2 * stadard_deviation))

		error = abs(1.0 - math.pow(basis, exponent))

		if max_value < error:
			max_value = error

		if min_value > error:
			min_value = error

		histogram[i] = error

	# scale error range
	for i in range(256):
		error = ((histogram[i] - min_value) / (max_value - min_value))
		histogram[i] = error

	return histogram


def get_contrast_histogram(grayscale_image):
	width, height = grayscale_image.size
	histogram = [0] * 256

	# count intensity values
	for x in range(width):
		for y in range(height):
			value = int(math.floor(pw.get_pixel(grayscale_image, x, y)[0]))
			histogram[value] += 1

	max_value = float('-inf')
	min_value = float('inf')

	# find min and max
	for i in range(256):
		value = histogram[i]

		if max_value < value:
			max_value = value

		if min_value > value:
			min_value = value

	# scale error range
	for i in range(256):
		ratio = ((histogram[i] - min_value) / (max_value - min_value))
		histogram[i] = (1 - ratio)

	return histogram


def get_frequency_histogram(grayscale_image):
	width, height = grayscale_image.size
	histogram = [0] * 256

	# number of color channels
	channel_count = len(grayscale_image.getbands())

	# count intensity values
	for x in range(width):
		for y in range(height):
			value = int(math.floor(pw.get_pixel(grayscale_image, x, y)[0]))
			histogram[value] += 1

	return histogram


def get_percentage_histogram(grayscale_image):
	frequency_histogram = get_frequency_histogram(grayscale_image)

	# Get size
	width, height = grayscale_image.size

	pixel_count = width * height

	percent_per_pixel = 100 / pixel_count

	percentage_histogram = [0] * 256
	percentage_histogram[0] = frequency_histogram[0] * percent_per_pixel

	for i in range(len(percentage_histogram)):
		percentage_histogram[i] = percentage_histogram[i - 1] + (frequency_histogram[i] * percent_per_pixel)

	return percentage_histogram


def get_intensity_at_percentage(percentage_histogram, percent):
	for i in range(len(percentage_histogram)):
		if percentage_histogram[i] >= percent:
			return i

	return (percentage_histogram[len(percentage_histogram) - 1] / 100) * 255.0


def normalize_intensity(intensity, min_intensity, max_intensity):
	if (max_intensity - min_intensity) == 0:
		return 0

	min_intensity = round(min_intensity)
	max_intensity = round(max_intensity)
	mino = 0
	maxo = 255

	return round((intensity - min_intensity) * (((maxo - mino) / (max_intensity - min_intensity)) + mino))


def normalize_red(intensity):
	mini = 86
	maxi = 230
	mino = 0
	maxo = 255

	return (intensity - mini) * (((maxo - mino) / (maxi - mini)) + mino)


def normalize_green(intensity):
	mini = 90
	maxi = 225
	mino = 0
	maxo = 255

	return (intensity - mini) * (((maxo - mino) / (maxi - mini)) + mino)


def normalize_blue(intensity):
	mini = 100
	maxi = 210
	mino = 0
	maxo = 255

	return (intensity - mini) * (((maxo - mino) / (maxi - mini)) + mino)
