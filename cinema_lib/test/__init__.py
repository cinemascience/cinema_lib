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
from functools import reduce
import filecmp
        
TEST_PATH = "cinema_lib/test/data"

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
        self.assertEqual(next(it), ("phi", "theta", "FILE"))
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

    def test_sphere_whitespace(self):
        self.assertTrue(d.check_database(self.SPHERE_DATA, "whitespace.csv"))

    def test_sphere_whitespace_file(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "whitespace_file.csv"))

    def test_sphere_proper_quoted(self):
        self.assertTrue(d.check_database(self.SPHERE_DATA, "proper_quoted.csv"))

    def test_sphere_improper_quoted_header(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "improper_quoted_header.csv"))

    def test_sphere_improper_quoted_row_1(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "improper_quoted_row_1.csv"))

    def test_sphere_improper_quoted_row_2(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "improper_quoted_row_2.csv"))

    def test_sphere_improper_quoted_header_alt(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "improper_quoted_header_alt.csv"))

    def test_sphere_improper_quoted_row_1_alt(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "improper_quoted_row_1_alt.csv"))

    def test_sphere_improper_quoted_row_2_alt(self):
        self.assertFalse(d.check_database(self.SPHERE_DATA, "improper_quoted_row_2_alt.csv"))


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

class BackupD(unittest.TestCase):
    """
    Test backing up a Spec D file.
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
        self.d_csv = os.path.join(self.SPHERE_DATA, d.SPEC_D_CSV_FILENAME)
        self.d_backup = os.path.join(self.SPHERE_DATA, "csv.good")
        sh.copyfile(self.d_csv, self.d_backup)
        os.unlink(self.d_csv)

    def tearDown(self):
        sh.rmtree(self.SPHERE_DATA)

    def test_default_backup(self):
        sh.copyfile(self.d_backup, self.d_csv)
        self.assertTrue(os.path.isfile(
            os.path.join(self.SPHERE_DATA, d.SPEC_D_CSV_FILENAME)))
        backup_fn = d.move_to_backup(self.SPHERE_DATA)
        self.assertTrue(os.path.isfile(
            os.path.join(self.SPHERE_DATA, backup_fn)))
        self.assertFalse(os.path.isfile(
            os.path.join(self.SPHERE_DATA, d.SPEC_D_CSV_FILENAME)))
        self.assertTrue(filecmp.cmp(self.d_backup,
            os.path.join(self.SPHERE_DATA, backup_fn), False))
        os.unlink(os.path.join(self.SPHERE_DATA, backup_fn))

    def test_alt_backup(self):
        other_fn = "other_db.foo"
        full_other = os.path.join(self.SPHERE_DATA, other_fn)
        sh.copyfile(self.d_backup, full_other)
        self.assertTrue(os.path.isfile(full_other))
        backup_fn = d.move_to_backup(self.SPHERE_DATA, other_fn)
        self.assertTrue(os.path.isfile(
            os.path.join(self.SPHERE_DATA, backup_fn)))
        self.assertFalse(os.path.isfile(full_other))
        self.assertTrue(filecmp.cmp(self.d_backup,
            os.path.join(self.SPHERE_DATA, backup_fn), False))
        os.unlink(os.path.join(self.SPHERE_DATA, backup_fn))

class AddColumnD(unittest.TestCase):
    """
    Add column tests for Spec D.
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
        self.d_csv = os.path.join(self.SPHERE_DATA, d.SPEC_D_CSV_FILENAME)
        self.d_backup = os.path.join(self.SPHERE_DATA, "csv.good")
        sh.copyfile(self.d_csv, self.d_backup)
        os.unlink(self.d_csv)

    def tearDown(self):
        sh.rmtree(self.SPHERE_DATA)

    def test_plus_one(self):
        sh.copyfile(self.d_backup, self.d_csv)
        backup = d.add_column_by_row_data(self.SPHERE_DATA, "phi plus one",
                                          lambda x: str(int(x[1]) + 1))
        backup_db = os.path.join(self.SPHERE_DATA, backup)
        self.assertTrue(filecmp.cmp(backup_db, self.d_backup, False))
        new_db = d.get_iterator(self.SPHERE_DATA)
        header = next(new_db)
        self.assertEqual(header, ("theta","phi","phi plus one","FILE"))
        self.assertTrue(reduce(
                        lambda x, y: x and (int(y[1]) + 1 == int(y[2])),
                        new_db, True))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        new_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, new_db, 0) == 21)
        os.unlink(self.d_csv)

    def test_create_new_files(self):
        sh.copyfile(self.d_backup, self.d_csv)
        def create_file(row):
            fn = row[-1] + ".foo"
            full = os.path.join(self.SPHERE_DATA, fn)
            open(full, "w").close()
            return fn
        backup = d.add_column_by_row_data(self.SPHERE_DATA, "FILE", 
                                          create_file)
        backup_db = os.path.join(self.SPHERE_DATA, backup)
        self.assertTrue(filecmp.cmp(backup_db, self.d_backup, False))
        new_db = d.get_iterator(self.SPHERE_DATA)
        header = next(new_db)
        self.assertEqual(header, ("theta","phi","FILE","FILE"))
        self.assertTrue(reduce(
                        lambda x, y: x and (y[2] + ".foo" == y[3]),
                        new_db, True))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        new_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, new_db, 0) == 21)
        os.unlink(self.d_csv)

    def test_plus_one_plus_two(self):
        sh.copyfile(self.d_backup, self.d_csv)
        backup = d.add_columns_by_row_data(self.SPHERE_DATA, 
                ("phi plus one", "phi plus two"),
                lambda x: (str(int(x[1]) + 1),str(int(x[1]) + 2)))
        backup_db = os.path.join(self.SPHERE_DATA, backup)
        self.assertTrue(filecmp.cmp(backup_db, self.d_backup, False))
        new_db = d.get_iterator(self.SPHERE_DATA)
        header = next(new_db)
        self.assertEqual(header, ("theta","phi",
                                  "phi plus one","phi plus two","FILE"))
        self.assertTrue(reduce(
                        lambda x, y: x and 
                                     (int(y[1]) + 1 == int(y[2])) and
                                     (int(y[1]) + 2 == int(y[3])),
                        new_db, True))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        new_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, new_db, 0) == 21)
        os.unlink(self.d_csv)

    def test_create_multiple(self):
        sh.copyfile(self.d_backup, self.d_csv)
        def create_data(row):
            fn_a = row[-1] + ".foo"
            full_a = os.path.join(self.SPHERE_DATA, fn_a)
            fn_b = row[-1] + ".bar"
            full_b = os.path.join(self.SPHERE_DATA, fn_b)
            open(full_a, "w").close()
            open(full_b, "w").close()
            return (str(int(row[1]) + 1), str(int(row[1]) + 2), fn_a, fn_b)
        backup = d.add_columns_by_row_data(self.SPHERE_DATA, 
                                           ("phi plus one",
                                            "phi plus two",
                                            "FILE", "FILE"),
                                           create_data)
        backup_db = os.path.join(self.SPHERE_DATA, backup)
        self.assertTrue(filecmp.cmp(backup_db, self.d_backup, False))
        new_db = d.get_iterator(self.SPHERE_DATA)
        header = next(new_db)
        self.assertEqual(header, ("theta","phi",
                                  "phi plus one", "phi plus two",
                                  "FILE","FILE","FILE"))
        self.assertTrue(reduce(
                        lambda x, y: x and 
                                     (y[4] + ".foo" == y[5]) and
                                     (y[4] + ".bar" == y[6]) and
                                     int(y[1]) + 1 == int(y[2]) and
                                     int(y[1]) + 2 == int(y[3]),
                        new_db, True))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        new_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, new_db, 0) == 21)
        os.unlink(self.d_csv)

    def test_create_new_files_new_files(self):
        sh.copyfile(self.d_backup, self.d_csv)
        def create_files(row):
            fn_a = row[-1] + ".foo"
            full_a = os.path.join(self.SPHERE_DATA, fn_a)
            fn_b = row[-1] + ".bar"
            full_b = os.path.join(self.SPHERE_DATA, fn_b)
            open(full_a, "w").close()
            open(full_b, "w").close()
            return (fn_a, fn_b)
        backup = d.add_columns_by_row_data(self.SPHERE_DATA, 
                                           ("FILE", "FILE"),
                                           create_files)
        backup_db = os.path.join(self.SPHERE_DATA, backup)
        self.assertTrue(filecmp.cmp(backup_db, self.d_backup, False))
        new_db = d.get_iterator(self.SPHERE_DATA)
        header = next(new_db)
        self.assertEqual(header, ("theta","phi","FILE","FILE","FILE"))
        self.assertTrue(reduce(
                        lambda x, y: x and 
                                     (y[2] + ".foo" == y[3]) and
                                     (y[2] + ".bar" == y[4]),
                        new_db, True))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        new_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, new_db, 0) == 21)
        os.unlink(self.d_csv)

class ImageTests(unittest.TestCase):
    """
    Image tests.
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

        # regression data
        self.GREY_DATA = "image_grey_data.csv"
        self.MEAN_DATA = "image_mean_data.csv"
        self.STDDEV_DATA = "image_stddev_data.csv"
        self.ENTROPY_DATA = "image_entropy_data.csv"
        self.UNIQUE_DATA = "image_unique_data.csv"
        self.CANNY_DATA = "image_canny_data.csv"
        self.PERCENTILE_DATA = "image_percentile_data.csv"
        self.JOINT_DATA = "image_joint_data.csv"
     
        # make some backups
        self.a_json = os.path.join(self.SPHERE_DATA, a.SPEC_A_JSON_FILENAME)
        self.d_csv = os.path.join(self.SPHERE_DATA, d.SPEC_D_CSV_FILENAME)
        self.d_backup = os.path.join(self.SPHERE_DATA, "csv.good")
        sh.copyfile(self.d_csv, self.d_backup)
        os.unlink(self.d_csv)

    def tearDown(self):
        sh.rmtree(self.SPHERE_DATA)

    def test_file_add_column(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return

        from .. import image
        from ..image import d as d_image

        def copyfile(b, a):
            one = os.path.join(b, a)
            two = os.path.join(b, a + ".foo")
            sh.copyfile(one, two)
            return a + ".foo"

        sh.copyfile(self.d_backup, self.d_csv)

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "FILE", copyfile, n_components=0))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "FILE", "FILE"))

        for row in d_db:
            left = os.path.join(self.SPHERE_DATA, row[2])
            right = os.path.join(self.SPHERE_DATA, row[3])
            self.assertTrue(filecmp.cmp(left, right, False))
            self.assertTrue(left + ".foo" == right)

        def compute(b, a):
            return (len(a),)
        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 3,
            "compute", compute, n_components=1))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "compute 0", 
            "FILE", "FILE"))

        for row in d_db:
            self.assertTrue(int(row[2]) == len(row[4]))

        def failure(b, a):
            raise Exception("foo")
        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 4,
            "failure", failure, fill="bar"))
        self.assertTrue(d.check_database(self.SPHERE_DATA))
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "compute 0", 
            "failure 0", "failure 1", "failure 2", "FILE", "FILE"))

        for row in d_db:
            self.assertTrue(row[3] == "bar")
            self.assertTrue(row[4] == "bar")
            self.assertTrue(row[5] == "bar")

        os.unlink(self.d_csv)

    def test_grey(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        a_grey = {}
        for row in a_db:
            new_fn = \
                image.file_grey(self.SPHERE_DATA, row[-1], suffix="_a")
            a_grey[row[-1]] = new_fn

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "FILE", image.file_grey, n_components=0))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "FILE", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.GREY_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            left = os.path.join(self.SPHERE_DATA, a_grey[row[2]])
            right = os.path.join(self.SPHERE_DATA, row[3])
            reg_image = os.path.join(self.SOURCE_DATA, reg_row[3])
            self.assertTrue(filecmp.cmp(left, right, False))
            self.assertEqual(row, reg_row)
            self.assertTrue(filecmp.cmp(right, reg_image, False))

        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, os.path.join(self.SOURCE_DATA, self.GREY_DATA))
#        regress = d.get_iterator(self.SPHERE_DATA)
#        next(regress)
#        for row in regress:
#            sh.copyfile(os.path.join(self.SPHERE_DATA, row[3]),
#                        os.path.join(self.SOURCE_DATA, row[3]))

        os.unlink(self.d_csv)

    def test_mean(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        means = {}
        for row in a_db:
            means[row[-1]] = image.file_mean(self.SPHERE_DATA, row[-1])

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "mean", image.file_mean))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "mean 0",
            "mean 1", "mean 2", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.MEAN_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            m = means[row[5]]
            self.assertTrue((m[0] - 1e-08  < float(row[2])) and
                            (float(row[2]) < m[0] + 1e-08 ))
            self.assertTrue(row[2] != "NaN")
            self.assertTrue((m[1] - 1e-08  < float(row[3])) and
                            (float(row[3]) < m[1] + 1e-08 ))
            self.assertTrue(row[3] != "NaN")
            self.assertTrue((m[2] - 1e-08  < float(row[4])) and
                            (float(row[4]) < m[2] + 1e-08 ))
            self.assertTrue(row[4] != "NaN")
            self.assertEqual(row, reg_row)
        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, os.path.join(self.SOURCE_DATA, self.MEAN_DATA))

        os.unlink(self.d_csv)

    def test_stddev(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        means = {}
        for row in a_db:
            means[row[-1]] = image.file_stddev(self.SPHERE_DATA, row[-1])

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "stddev", image.file_stddev))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "stddev 0",
            "stddev 1", "stddev 2", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.STDDEV_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            m = means[row[5]]
            self.assertTrue((m[0] - 1e-08  < float(row[2])) and
                            (float(row[2]) < m[0] + 1e-08 ))
            self.assertTrue(row[2] != "NaN")
            self.assertTrue((m[1] - 1e-08  < float(row[3])) and
                            (float(row[3]) < m[1] + 1e-08 ))
            self.assertTrue(row[3] != "NaN")
            self.assertTrue((m[2] - 1e-08  < float(row[4])) and
                            (float(row[4]) < m[2] + 1e-08 ))
            self.assertTrue(row[4] != "NaN")
            self.assertEqual(row, reg_row)
        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, 
#                os.path.join(self.SOURCE_DATA, self.STDDEV_DATA))

        os.unlink(self.d_csv)

    def test_entropy(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        means = {}
        for row in a_db:
            means[row[-1]] = image.file_shannon_entropy(
                    self.SPHERE_DATA, row[-1])

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "entropy", image.file_shannon_entropy))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "entropy 0",
            "entropy 1", "entropy 2", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.ENTROPY_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            m = means[row[5]]
            self.assertTrue((m[0] - 1e-08  < float(row[2])) and
                            (float(row[2]) < m[0] + 1e-08 ))
            self.assertTrue(row[2] != "NaN")
            self.assertTrue((m[1] - 1e-08  < float(row[3])) and
                            (float(row[3]) < m[1] + 1e-08 ))
            self.assertTrue(row[3] != "NaN")
            self.assertTrue((m[2] - 1e-08  < float(row[4])) and
                            (float(row[4]) < m[2] + 1e-08 ))
            self.assertTrue(row[4] != "NaN")
            self.assertEqual(row, reg_row)
        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, 
#                os.path.join(self.SOURCE_DATA, self.ENTROPY_DATA))

        os.unlink(self.d_csv)

    def test_unique(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        means = {}
        for row in a_db:
            means[row[-1]] = image.file_unique_count(self.SPHERE_DATA, row[-1])

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "unique", image.file_unique_count, n_components=0))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "unique", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.UNIQUE_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            m = means[row[3]]
            self.assertTrue(m == int(row[2]))
            self.assertEqual(row, reg_row)
        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, 
#                os.path.join(self.SOURCE_DATA, self.UNIQUE_DATA))

        os.unlink(self.d_csv)

    def test_canny(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        means = {}
        for row in a_db:
            means[row[-1]] = image.file_canny_count(self.SPHERE_DATA, row[-1])

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "canny", image.file_canny_count))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "canny 0", 
            "canny 1", "canny 2", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.CANNY_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            m = means[row[5]]
            self.assertTrue(m[0] == int(row[2]))
            self.assertTrue(row[2] != "NaN")
            self.assertTrue(m[1] == int(row[3]))
            self.assertTrue(row[3] != "NaN")
            self.assertTrue(m[2] == int(row[4]))
            self.assertTrue(row[4] != "NaN")
            self.assertEqual(row, reg_row)
        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, 
#                os.path.join(self.SOURCE_DATA, self.CANNY_DATA))

        os.unlink(self.d_csv)

    def test_percentile(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        means = {}
        for row in a_db:
            means[row[-1]] = image.file_percentile(
                    self.SPHERE_DATA, row[-1], 99)

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "percentile", lambda x, y: image.file_percentile(x, y, 99)))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "percentile 0",
            "percentile 1", "percentile 2", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.PERCENTILE_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            m = means[row[5]]
            self.assertTrue((m[0] - 1e-08  < float(row[2])) and
                            (float(row[2]) < m[0] + 1e-08 ))
            self.assertTrue(row[2] != "NaN")
            self.assertTrue((m[1] - 1e-08  < float(row[3])) and
                            (float(row[3]) < m[1] + 1e-08 ))
            self.assertTrue(row[3] != "NaN")
            self.assertTrue((m[2] - 1e-08  < float(row[4])) and
                            (float(row[4]) < m[2] + 1e-08 ))
            self.assertTrue(row[4] != "NaN")
            self.assertEqual(row, reg_row)
        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, 
#                os.path.join(self.SOURCE_DATA, self.PERCENTILE_DATA))

        os.unlink(self.d_csv)

    def test_joint(self):
        try:
            import skimage
            from .. import image
        except Exception as e:
            log.info("Unable to run test: " + str(e))
            return
       
        from .. import image
        from skimage import io
        from ..image import d as d_image

        sh.copyfile(self.d_backup, self.d_csv)
        a_db = a.get_iterator(self.SPHERE_DATA)

        next(a_db)
        means = {}
        for row in a_db:
            means[row[-1]] = image.file_joint_entropy(
                    self.SPHERE_DATA, row[-1])

        self.assertFalse(d_image.file_add_column(self.SPHERE_DATA, 2,
            "joint entropy", image.file_joint_entropy, n_components=0))

        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertTrue(reduce(lambda x, y: x + 1, d_db, 0) == 21)
        d_db = d.get_iterator(self.SPHERE_DATA)
        self.assertEqual(next(d_db), ("theta", "phi", "joint entropy", "FILE"))

        regress = d.get_iterator(self.SOURCE_DATA, self.JOINT_DATA)
        next(regress)

        for row, reg_row in zip(d_db, regress):
            m = means[row[3]]
            self.assertTrue((m - 1e-08  < float(row[2])) and
                            (float(row[2]) < m + 1e-08 ))
            self.assertTrue(row[2] != "NaN")
            self.assertEqual(row, reg_row)
        self.assertTrue(d.check_database(self.SPHERE_DATA))

#        # uncomment when you want to regenerate the regression data
#        sh.copyfile(self.d_csv, 
#                os.path.join(self.SOURCE_DATA, self.JOINT_DATA))

        os.unlink(self.d_csv)

