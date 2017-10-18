*Cinema* library (*cinema_lib*)

*cinema_lib* is a set of tools and library for interacting with a Cinema 
database (currently Spec A and Spec D) through Python and the command line
tool, *cinema*.

To run the command line tool directly from the repository:
```
$ git clone <cinema_lib>
$ cd <cinema_lib>
$ ./cinema
```

To install with *pip* after cloning:
```
$ git clone <cinema_lib>
$ cd <cinema_lib>
$ pip install .
```

Current requirements are:
- Python 3.6

Current capabilities:
- Validate a Spec A database
- Validate a Spec D database
- Convert Spec A to Spec D
- Convert Spec D to SQLite
