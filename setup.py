from setuptools import setup
import unittest 
from cinema_lib import version

def readme():
    with open('README.md') as f:
        return f.read()

def tests():
    loader = unittest.TestLoader()
    return loader.discover('cinema_lib.test')

setup(name='cinema_lib',
      version=version(),
      description="Library for Cinema databases",
      long_description=readme(),
      test_suite='setup.tests',
      zip_safe=False,
      entry_points={
          'console_scripts': ['cinema = cinema_lib.cl:main']
          },
      packages=['cinema_lib']
      )
