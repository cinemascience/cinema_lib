"""
Utility library for Cinema databases.

The various submodules are:
    cinema.cl: command line utility for library functions
    cinema.spec: utilities for specifications
    cinema.spec.a: utilities for Spec A
    cinema.spec.d: utilities for Spec D
    cinema.test: unit and regression testing
    cinema.image: utilities for processing image columns
"""

def version():
    return "0.7.1"

def check_numpy_version(np):
    try:
        ver = np.version.version.split('.')
        if int(ver[0]) < 1:
            raise Exception("numpy version needs to be 1.13 or greater: {0}".format(np.version.version))
        elif int(ver[0]) == 1 and int(ver[1]) < 13:
            raise Exception("numpy version needs to be 1.13 or greater: {0}".format(np.version.version))
    except Exception as e:
        raise e

