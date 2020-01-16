## *Cinema* library (*cinema_lib*)

*cinema_lib* is a set of tools and library for interacting with a Cinema 
database (currently Spec A and Spec D) through Python and the command line 
tool, *cinema*.

### Requirements

Minimum requirements are:
- Python 3.6
- numpy >=1.13
  - image capabilities
  - OpenCV capabilities
- scikit-image >=0.13.1 (newer versions may cause regression tests to fail
  due to changing numerics and implementations of algorithms)
  - image capabilities

Optional requirements are:
- opencv-python >=3.4 (newer versions may cause regression tests to fail
  due to changing numerics)
  - OpenCV capabilities

### Installation

This command will install cinema_lib in your current directory:
With [curl](https://curl.haxx.se/):
```
curl -s "https://raw.githubusercontent.com/EthanS94/cinema_lib/install_script/install.sh" | sh
```

With [wget](https://www.gnu.org/software/wget/):
```
wget -qO - "https://raw.githubusercontent.com/EthanS94/cinema_lib/install_script/install.sh" | sh
```

To run the command line tool directly from the repository, after cloning:
```
$ git clone https://github.com/cinemascience/cinema_lib.git 
$ cd cinema_lib
$ ./cinema
```

To install with *pip*:
```
$ git clone https://github.com/cinemascience/cinema_lib.git
$ cd cinema_lib
$ pip install .
$ cinema
```

### Examples (directly found by running `cinema --help`)

#### Help

`$ cinema --help`
- get all of the currently implemented commands

#### Database manipulation
`$ cinema -t -a cinema_lib/test/data/sphere.cdb`
- validate a Spec A database

`$ cinema -i -d cinema_lib/test/data/sphere.cdb`
- return the header (parameters, columns) for a Spec D database

`$ cinema -itvq -d cinema_lib/test/data/sphere.cdb`
- quickly validate a Spec D database and report the header, verbosely

`$ cinema -t --a2d -a cinema_lib/test/data/sphere.cdb`
- validate a Spec A database and convert it to a Spec D database

#### Image examples
`$ cinema -d cinema_lib/test/data/sphere.cdb --image-grey 2`
- convert RGB images to greyscale images

`$ cinema -d cinema_lib/test/data/sphere.cdb --image-mean 2 --label average`
- calculate the average color per component in images, naming the column
  "average"

#### Computer vision examples
`$ cinema -d cinema_lib/test/data/sphere.cdb --cv-gaussian-blur 2`
- convert apply a Gaussian blur to images

`$ cinema -d cinema_lib/test/data/sphere.cdb --cv-fast-draw 2 --label FAST`
- draw locations of FAST features in images, naming the column "FILE FAST"

