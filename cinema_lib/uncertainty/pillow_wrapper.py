from PIL import Image
from PIL import ImageChops
from PIL import ImageStat


# Load Image
def open_image(path):
	newImage = Image.open(path)
	return newImage


# Save Image
def save_image(image, path):
	image.save(path, 'png')


# Create a new image with the given size
def create_image(i, j):
	image = Image.new("RGB", (i, j), "white")
	return image

def create_image_greyscale(i, j):
	image = Image.new("L", (i, j), "white")
	return image


def merge_image(bandr, bandg, bandb):
	return Image.merge("RGB", (bandr, bandg, bandb))


def get_diff_image(img1, img2):
	return ImageChops.difference(img1, img2)


def get_image_extrema(image):
	return image.getextrema()


# Get the pixel from the given image
def get_pixel(image, i, j):
	# Inside image bounds?
	width, height = image.size
	if i > width or j > height:
		return None

	# number of color channels
	channel_count = len(image.getbands())

	# Get Pixel
	pixel = image.getpixel((i, j))
	if channel_count > 1:
		return pixel
	else:
		return [pixel]


# Create a Grayscale version of the image
def convert_grayscale(image):
	# number of color channels
	channel_count = len(image.getbands())

	if channel_count == 1:
		return image

	# Get size
	width, height = image.size

	# Create new Image and a Pixel Map
	garyscaleimage = create_image(width, height)
	pixels = garyscaleimage.load()

	# Transform to grayscale
	for i in range(width):
		for j in range(height):
			# Get Pixel
			pixel = get_pixel(image, i, j)

			# Get R, G, B values (This are int from 0 to 255)
			red = pixel[0]
			green = pixel[1]
			blue = pixel[2]

			# Transform to grayscale
			gray = (red * 0.299) + (green * 0.587) + (blue * 0.114)

			# Set Pixel in new image
			pixels[i, j] = (int(gray), int(gray), int(gray))

	# Return new image
	return garyscaleimage
