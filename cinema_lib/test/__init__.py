"""
Unit/regression testing for clib.
"""

from ..spec import a
from ..spec import d
from .. import spec

import os
import logging as log
import unittest
import inspect
import tempfile as temp
import shutil as sh
        
TEST_PATH = "cinemalib/test/data"

def unittest_verbosity():
    frame = inspect.currentframe()
    while frame:
        self = frame.f_locals.get('self')
        if isinstance(self, unittest.TestProgram):
            return self.verbosity
        frame = frame.f_back
    return 0

class SpecA(unittest.TestCase):
    """
    Tests for the clib.spec.a module.

    check_database will check most of the functionality found within
    the spec A, because it uses get_iterator and get_dictionary.
    """

    def setUp(self):
        if unittest_verbosity() > 1:
            log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=log.DEBUG, datefmt='%I:%M:%S')
        else:
            log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=60, datefmt='%I:%M:%S')

        self.SPHERE_DATA = os.path.join(TEST_PATH, "sphere.cdb")

    def test_sphere(self):
        self.assertTrue(a.check_database(self.SPHERE_DATA)) 

    def test_sphere_quick(self, quick=True):
        self.assertTrue(a.check_database(self.SPHERE_DATA)) 

    def test_sphere_no_meta(self):
        self.assertFalse(a.check_database(self.SPHERE_DATA, "no_meta.json"))

    def test_sphere_missing_file(self):
        self.assertFalse(a.check_database(self.SPHERE_DATA, "missing_no.json"))

    def test_sphere_no_data(self):
        self.assertFalse(a.check_database(self.SPHERE_DATA, "no_data.json"))

    def test_sphere_no_files(self):
        self.assertFalse(a.check_database(self.SPHERE_DATA, "no_files.json"))

    def test_sphere_no_files_quick(self, quick=True):
        self.assertTrue(a.check_database(self.SPHERE_DATA, "no_files.json",
                        quick=True)) 

    def test_sphere_iterator(self):
        it = a.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(it), ("theta", "phi", "FILE"))
        self.assertEqual(len([i for i in it]), 20)

    def test_sphere_wrong_filetype(self):
        self.assertFalse(a.check_database(self.SPHERE_DATA, 
                         d.SPEC_D_CSV_FILENAME))

    def test_sphere_dictionary(self):
        it = a.get_dictionary(self.SPHERE_DATA)
        check = a.KEY_ARGUMENTS in it
        self.assertTrue(check)
        if check:
            check = "phi" in it[a.KEY_ARGUMENTS]
            self.assertTrue(check)
            if check:
                self.assertTrue(
                  a.KEY_ARG_DEFAULT in it[a.KEY_ARGUMENTS]["phi"])
                self.assertTrue(
                  a.KEY_ARG_LABEL in it[a.KEY_ARGUMENTS]["phi"])
                self.assertTrue(
                  a.KEY_ARG_TYPE in it[a.KEY_ARGUMENTS]["phi"])
                self.assertTrue(
                  a.KEY_ARG_VALUES in it[a.KEY_ARGUMENTS]["phi"])
            check = "theta" in it[a.KEY_ARGUMENTS]
            self.assertTrue(check)
            if check:
                self.assertTrue(
                  a.KEY_ARG_DEFAULT in it[a.KEY_ARGUMENTS]["theta"])
                self.assertTrue(
                  a.KEY_ARG_LABEL in it[a.KEY_ARGUMENTS]["theta"])
                self.assertTrue(
                  a.KEY_ARG_TYPE in it[a.KEY_ARGUMENTS]["theta"])
                self.assertTrue(
                  a.KEY_ARG_VALUES in it[a.KEY_ARGUMENTS]["theta"])
        check = a.KEY_METADATA in it
        self.assertTrue(check)
        if check:
            check = a.KEY_METADATA_TYPE in it[a.KEY_METADATA]
            self.assertTrue(check)
            if check:
                self.assertTrue(it[a.KEY_METADATA][a.KEY_METADATA_TYPE] ==
                    a.VALUE_METADATA_TYPE)
        check = a.KEY_VERSION in it
        self.assertTrue(check)
        if check:
            self.assertTrue(it[a.KEY_VERSION] == a.VALUE_VERSION)
        check = a.KEY_TYPE in it
        self.assertTrue(check)
        if check:
            self.assertTrue(it[a.KEY_TYPE] == a.VALUE_TYPE)
        self.assertTrue(a.KEY_NAME_PATTERN in it)

class SpecD(unittest.TestCase):
    """
    Tests for the clib.spec.d module.

    check_database will check most of the functionality found within
    the spec D, because it uses get_iterator.
    """

    def setUp(self):
        if unittest_verbosity() > 1:
            log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=log.DEBUG, datefmt='%I:%M:%S')
        else:
            log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=60, datefmt='%I:%M:%S')

        self.SPHERE_DATA = os.path.join(TEST_PATH, "sphere.cdb")

    def test_sphere(self):
        self.assertTrue(d.check_database(self.SPHERE_DATA)) 

    def test_sphere_quick(self, quick=True):
        self.assertTrue(d.check_database(self.SPHERE_DATA)) 

    def test_sphere_typecheck(self):
        self.assertTrue(d.check_database(self.SPHERE_DATA, "typecheck.csv")) 

    def test_sphere_missing_file(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "missing_no.csv"))

    def test_sphere_no_data(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "no_data.csv"))

    def test_sphere_no_files(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "no_files.csv"))

    def test_sphere_no_files_quick(self, quick=True):
        self.assertTrue(d.check_database(self.SPHERE_DATA, "no_files.csv",
                        quick=True)) 

    def test_sphere_iterator(self):
        it = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(it), ("theta", "phi", "FILE"))
        self.assertEqual(len([i for i in it]), 20)

    def test_sphere_wrong_filetype(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, 
                         a.SPEC_A_JSON_FILENAME))

    def test_sphere_wrong_types(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "wrong_types.csv"))

    def test_sphere_empty(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "empty.csv"))

    def test_sphere_wrong_number(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "wrong_num1.csv"))
        self.assertFalse(d.check_database(self.SPHERE_DATA, "wrong_num2.csv"))

    def test_sphere_nan(self):
        self.assertTrue(d.check_database(self.SPHERE_DATA, "nan.csv"))

    def test_sphere_wrong_file(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "wrong_file.csv"))

    def test_sphere_no_header(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "no_header.csv"))

class Convert(unittest.TestCase):
    """
    Conversion tests for the clib.spec module.
    """

    def setUp(self):
        if unittest_verbosity() > 1:
            log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=log.DEBUG, datefmt='%I:%M:%S')
        else:
            log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=60, datefmt='%I:%M:%S')

        # copy files to tmp
        self.SOURCE_DATA = os.path.join(TEST_PATH, "sphere.cdb")
        self.TEMP_PATH = temp.mkdtemp()
        self.SPHERE_DATA = os.path.join(self.TEMP_PATH, "sphere.cdb")
        sh.copytree(self.SOURCE_DATA, self.SPHERE_DATA)
        self.SPHERE_TABLE = "sphere"
     
        # make some backups
        self.a_json = os.path.join(self.SPHERE_DATA, a.SPEC_A_JSON_FILENAME)
        self.d_csv = os.path.join(self.SPHERE_DATA, d.SPEC_D_CSV_FILENAME)
        self.a_backup = os.path.join(self.SPHERE_DATA, "json.good")
        self.d_backup = os.path.join(self.SPHERE_DATA, "csv.good")
        sh.copyfile(self.a_json, self.a_backup)
        sh.copyfile(self.d_csv, self.d_backup)
        os.unlink(self.a_json)
        os.unlink(self.d_csv)

    def tearDown(self):
        sh.rmtree(self.SPHERE_DATA)

    def test_convert_a_to_d(self):
        sh.copyfile(self.a_backup, self.a_json)
        self.assertTrue(spec.convert_a_to_d(self.SPHERE_DATA))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        self.assertFalse(spec.convert_a_to_d(self.SPHERE_DATA))
        os.unlink(self.d_csv)
        os.unlink(self.a_json)

    def test_sqlite3(self):
        sh.copyfile(self.d_backup, self.d_csv)
        db = d.get_sqlite3(self.SPHERE_DATA)
        self.assertTrue(db != None)
        log.info("Tables are:")
        for row in db.execute("SELECT * FROM sqlite_master"):
            log.info("{0}".format(row))
        fetch = db.\
          execute("SELECT COUNT(*) FROM %s" % self.SPHERE_TABLE).fetchone()
        self.assertTrue(fetch[0] == 20)
        fetch = db.execute("SELECT COUNT(*) FROM %s WHERE theta != 0" %
                self.SPHERE_TABLE).fetchone()
        self.assertTrue(fetch[0] == 0)
        fetch = db.execute("SELECT theta FROM %s WHERE phi = -180" %
                self.SPHERE_TABLE).fetchone()
        self.assertTrue(fetch[0] == 0)
        fetch = db.execute("SELECT COUNT(*) FROM %s WHERE phi > 0" %
                self.SPHERE_TABLE).fetchone()
        self.assertTrue(fetch[0] == 9)
        os.unlink(self.d_csv)
