*Cinema* library (*cinema_lib*)

*cinema_lib* is a set of tools and library for interacting with a Cinema 
database (currently Spec A and Spec D) through Python and the command line 
tool, *cinema*.

To run the command line tool directly from the repository, after cloning:
```
$ git clone https://github.com/lanl/cinema_lib.git
$ cd cinema_lib
$ ./cinema
```

To install with *pip*:
```
$ git clone https://github.com/lanl/cinema_lib.git
$ cd cinema_lib
$ pip install .
$ cinema
```

Minimum requirements are:
- Python 3.6

Optional requirements are:
- numpy >=1.13
  - image capabilities
  - OpenCV capabilities
- scikit-image >=0.13.1
  - image capabilities
- opencv-python >=3.4
  - OpenCV capabilities
