"""
Command line utility for Cinema clib. Execute with "python -m clib.cl"
"""

import logging as log
from .spec import d

# TODO move error strings to top
# TODO move informative messages to top

class ERROR_CODES:
  N_GREATER_THAN_N_COLUMNS = 1
  NO_INPUT_DATABASE_FOR_VALIDATION = 2
  SPEC_A_VALIDATION_FAILED = 3
  SPEC_D_VALIDATION_FAILED = 4
  CONVERSION_FROM_A_TO_D_FAILED = 5
  NO_INPUT_DATABASE_FOR_A_TO_D_CONVERSION = 6
  CONVERSION_FROM_D_TO_SQLITE_FAILED = 7
  NO_INPUT_DATABASE_FOR_D_TO_SQLITE_CONVERSION = 8
  NO_INPUT_DATABASE_FOR_IMAGE_COMMAND = 9
  IMAGE_MEAN_FAILED = 10
  IMAGE_GREY_FAILED = 11
  IMAGE_STDDEV_FAILED = 12
  IMAGE_ENTROPY_FAILED = 13
  IMAGE_UNIQUE_FAILED = 14
  IMAGE_CANNY_FAILED = 15
  N_IS_NOT_A_FILE_COLUMN = 16
  IMAGE_FIRSTQ_FAILED = 17
  IMAGE_SECONDQ_FAILED = 18
  IMAGE_THIRDQ_FAILED = 19
  IMAGE_90TH_FAILED = 20
  IMAGE_95TH_FAILED = 21
  IMAGE_99TH_FAILED = 22
  IMAGE_JOINT_FAILED = 23

def relabel(default, user, is_file=False):
    if is_file:
        if user == None:
            return "FILE" + default
        else:
            return "FILE" + user
    else:
        if user == None:
            return default
        else:
            return user

def check_n(header, n):
    if n >= len(header):
        log.error("N ({0}) is greater or equal to the number of columns in input database ({1}).".format(n, len(header)))
        exit(ERROR_CODES.N_GREATER_THAN_N_COLUMNS)
    files = d.file_columns(header)
    if n not in files:
        log.error("N ({0}) is not a FILE column.".format(n))
        exit(ERROR_CODES.N_IS_NOT_A_FILE_COLUMN)

def main():
    from . import spec
    from .spec import a
    from . import version

    import argparse
    import configparser
    import textwrap
    import os

    CL_VERSION = version()

    conf_parser = argparse.ArgumentParser(
        # Turn off help, so we print all options in response to -h
        add_help=False
        )

    args, remaining_argv = conf_parser.parse_known_args()

    epilog_text = textwrap.dedent(
"""
- Column numbers, N, are 0-indexed, i.e., 0, 1, 2, etc.
- Only one COMMAND can be run at a time.
- VALIDATE and FLAG can be run in conjunction with COMMAND or independently.\n\n
""")
    # try scikit-image
    skimage_ok = False
    try:
        import skimage
        import numpy
        skimage_ok = True

        from . import check_numpy_version
        check_numpy_version(numpy)

        epilog_text += textwrap.dedent(
"""
- Image functions require that the input database is Spec D. The database 
  (data.csv) will be backed up prior to running the command. Backup files
  can be found in the database directory as "data_csv.<timestamp>.<md5 hash>".
- Images in a column need to have the same number of components (grey, rgb, 
  rgba, etc.) and that there is an image file in the first data row to be 
  able to detect the number of components for the images.
- Functions run on multi-component images will operate per component, 
  returning the result per component, except for --image-unique and 
  --image-joint.\n\n
""")
    except Exception as e:
        epilog_text += textwrap.dedent(
        """
        Image functionality unavailable. Scikit-image and numpy required: 
        """ + str(e) + "\n\n")

    # examples
    epilog_text += textwrap.dedent(
"""
Examples:
$ cinema -t -a cinema_lib/test/data/sphere.cdb
    validate a Spec A database
$ cinema -i -d cinema_lib/test/data/sphere.cdb
    return the header (parameters, columns) for a Spec D database
$ cinema -itvq -d cinema_lib/test/data/sphere.cdb
    quickly validate a Spec D database and report the header, verbosely
$ cinema -t --a2d -a cinema_lib/test/data/sphere.cdb
    validate a Spec A database and convert it to a Spec D database\n\n
""")

    if skimage_ok:
        epilog_text += textwrap.dedent(
"""
Image examples:
$ cinema -d cinema_lib/test/data/sphere.cdb --image-grey 2
    convert RGB images to greyscale images
$ cinema -d cinema_lib/test/data/sphere.cdb --image-mean 2 --label average
    calculate the average color per component in images, naming them average
""")

    # Don't surpress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Inherit options from config_parser
        parents=[conf_parser],
        # print script description with -h/--help
        epilog=textwrap.dedent(epilog_text)
        )

    # parser.set_defaults(**defaults)
    parser.add_argument("--version", action="version", version=str(CL_VERSION))
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
            help="FLAG: report verbosely")
    parser.add_argument("-q", "--quick", action="store_true", default=False,
            help="FLAG: do not validate row data, if validating (--test)")
    parser.add_argument("-a", "--astaire", metavar="DB", type=str,
            help="INPUT: specify an input Spec A database")
    parser.add_argument("-d", "--dietrich", metavar="DB", type=str,
            help="INPUT: specify an input Spec D database")
    parser.add_argument("-l", "--label", metavar="STR", type=str,
            help="INPUT: specify a header (label) for new output columns, otherwise a default label is generated. if the column(s) are output files, FILE will be automatically prepended to the supplied label.")
    parser.add_argument("-t", "--test", action="store_true", default=False,
            help="VALIDATE: validate input databases. if used in combination with a COMMAND, will only continue processing if INPUT databases are valid")
    parser.add_argument("-i", "--info", action="store_true", default=False,
            help="VALIDATE: report the header (parameters) of the database")
    parser.add_argument("--a2d", "--astairetodietrich", action="store_true",
        default=False,
        help="COMMAND: convert a Spec D database to a Spec A database, in place")
    parser.add_argument("--d2s", "--dietrichtosqlite", action="store_true", 
        default=False,
        help="COMMAND: create a SQLite3 database from a Spec D database, to ./<database_name>.db")
    # add skimage tools
    if skimage_ok:
        parser.add_argument("--image-grey", metavar="N", type=int,
                help="COMMAND: convert and write image data to greyscale PNG in column number N, using Scikit-image color.rgb2grey. new files are named \"<old_base_filename>_grey.png\"")
        parser.add_argument("--image-mean", metavar="N", type=int,
                help="COMMAND: add image mean data calculated from images in column number N")
        parser.add_argument("--image-stddev", metavar="N", type=int,
                help="COMMAND: add image standard deviation data calculated from images in column number N")
        parser.add_argument("--image-unique", metavar="N", type=int,
                help="COMMAND: add unique pixel count data calculated from images in column number N")
        parser.add_argument("--image-entropy", metavar="N", type=int,
                help="COMMAND: add image Shannon entropy data calculated from images in column number N, using a histogram with 131072 bins")
        parser.add_argument("--image-joint", metavar="N", type=int,
                help="COMMAND: add the joint entropy (multi-dimensional Shannon entropy) data calculated from images in column number N, using 1024 discretization levels per dimension")
        parser.add_argument("--image-canny", metavar="N", type=int,
                help="COMMAND: add Canny edge pixel count data calculated from images in column number N")
        parser.add_argument("--image-firstq", metavar="N", type=int,
                help="COMMAND: add the first quartile data calculated from images in column number N")
        parser.add_argument("--image-secondq", metavar="N", type=int,
                help="COMMAND: add the second quartile data calculated from images in column number N")
        parser.add_argument("--image-thirdq", metavar="N", type=int,
                help="COMMAND: add the third quartile data calculated from images in column number N")
        parser.add_argument("--image-90th", metavar="N", type=int,
                help="command: add the 90th percentile data calculated from images in column number N")
        parser.add_argument("--image-95th", metavar="N", type=int,
                help="command: add the 95th percentile data calculated from images in column number N")
        parser.add_argument("--image-99th", metavar="N", type=int,
                help="command: add the 99th percentile data calculated from images in column number N")

    args = parser.parse_args(remaining_argv)

    # set up the proper reporting mode
    # log.info, log.warning, log.error
    if (args.verbose):
        log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', 
                        level=log.INFO, datefmt='%I:%M:%S')
    else:
        log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', 
                        level=log.WARNING, datefmt='%I:%M:%S')

    no_command = True
    checked_db = False
    # validate databases
    if args.test:
        if args.astaire is not None:
            if not a.check_database(args.astaire, quick=args.quick):
                exit(ERROR_CODES.SPEC_A_VALIDATION_FAILED)
            else:
                checked_db = True
        if args.dietrich is not None:
            if not d.check_database(args.dietrich, quick=args.quick):
                exit(ERROR_CODES.SPEC_D_VALIDATION_FAILED)
            else:
                checked_db = True
        if not checked_db:
            log.error("Input database not specified for validation.")
            exit(ERROR_CODES.NO_INPUT_DATABASE_FOR_VALIDATION)

    # report headers
    if args.info:
        if args.astaire is not None:
            a_db = a.get_iterator(args.astaire)
            if a_db == None:
                log.error("Unable to open database.")
                exit(ERROR_CODES.SPEC_A_VALIDATION_FAILED)
            else:
                header = next(a_db)
                for n, col in zip(range(0, len(header)), header):
                    print("{0}: {1}".format(n, col))
                checked_db = True
        if args.dietrich is not None:
            d_db = d.get_iterator(args.dietrich)
            if d_db == None:
                log.error("Unable to open database.")
                exit(ERROR_CODES.SPEC_D_VALIDATION_FAILED)
            else:
                header = next(d_db)
                for n, col in zip(range(0, len(header)), header):
                    print("{0}: {1}".format(n, col))
                checked_db = True
        if not checked_db:
            log.error("Input database not specified for validation.")
            exit(ERROR_CODES.NO_INPUT_DATABASE_FOR_VALIDATION)

    # convert A to D
    if args.a2d and no_command:
        if args.astaire is not None:
            if not spec.convert_a_to_d(args.astaire):
                exit(ERROR_CODES.CONVERSION_FROM_A_TO_D_FAILED)
            else:
                no_command = False

        if no_command:
            log.error("Input database not specified for A to D conversion.")
            exit(ERROR_CODES.NO_INPUT_DATABASE_FOR_A_TO_D_CONVERSION)
    
    # convert D to S
    if args.d2s and no_command:
        if args.dietrich is not None:
            if d.get_sqlite3(
                 args.d2s, where=os.path.splitext(
                 os.path.basename(
                 os.path.dirname(args.d2s)))[0] + ".db") == None:
                exit(ERROR_CODES.CONVERSION_FROM_D_TO_SQLITE_FAILED)
            else:
                no_command = False

        if no_command:
            log.error(
              "Input database not specified for D to SQLite conversion.")
            exit(ERROR_CODES.NO_INPUT_DATABASE_FOR_D_TO_SQLITE_CONVERSION)

    # image commands
    if skimage_ok:
        from .image import d as d_image
        from . import image

        # image command check
        image_command = \
            args.image_mean is not None or \
            args.image_grey is not None or \
            args.image_stddev is not None or \
            args.image_entropy is not None or \
            args.image_unique is not None or \
            args.image_canny is not None or \
            args.image_firstq is not None or \
            args.image_secondq is not None or \
            args.image_thirdq is not None or \
            args.image_90th is not None or \
            args.image_95th is not None or \
            args.image_99th is not None or \
            args.image_joint is not None

        if image_command and no_command:
            if args.dietrich is None:
                log.error(
                    "Input Spec D database not specified for image command.")
                exit(ERROR_CODES.NO_INPUT_DATABASE_FOR_IMAGE_COMMAND)
            else:
                no_command = False

                # check N
                header = next(d.get_iterator(args.dietrich))

                # image-mean
                if args.image_mean is not None:
                    check_n(header, args.image_mean)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_mean, 
                                               relabel(
                                                   "image mean", 
                                                   args.label),
                                               image.file_mean):
                        exit(ERROR_CODES.IMAGE_MEAN_FAILED)
                # image-grey
                elif args.image_grey is not None:
                    check_n(header, args.image_grey)
                    if d_image.file_add_column(args.dietrich,
                                               args.image_grey,
                                               relabel(
                                                   "greyscale",
                                                   args.label,
                                                   True),
                                               image.file_grey,
                                               n_components=0):
                        exit(ERROR_CODES.IMAGE_GREY_FAILED)
                # image-stddev
                elif args.image_stddev is not None:
                    check_n(header, args.image_stddev)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_stddev, 
                                               relabel(
                                                   "image standard deviation",
                                                   args.label),
                                               image.file_stddev):
                        exit(ERROR_CODES.IMAGE_STDDEV_FAILED)
                # image-entropy
                elif args.image_entropy is not None:
                    check_n(header, args.image_entropy)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_entropy, 
                                               relabel(
                                                   "image shannon entropy",
                                                   args.label),
                                               image.file_shannon_entropy):
                        exit(ERROR_CODES.IMAGE_ENTROPY_FAILED)
                # image-unique
                elif args.image_unique is not None:
                    check_n(header, args.image_unique)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_unique, 
                                               relabel(
                                                   "image unique count",
                                                   args.label),
                                               image.file_unique_count,
                                               n_components=0):
                        exit(ERROR_CODES.IMAGE_UNIQUE_FAILED)
                # image-canny
                elif args.image_canny is not None:
                    check_n(header, args.image_canny)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_canny, 
                                               relabel(
                                                   "image canny count",
                                                   args.label),
                                               image.file_canny_count):
                        exit(ERROR_CODES.IMAGE_CANNY_FAILED)
                # image-firstq
                elif args.image_firstq is not None:
                    check_n(header, args.image_firstq)
                    __firstq = lambda x, y: image.file_percentile(x, y, 25)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_firstq, 
                                               relabel(
                                                   "image first quartile",
                                                   args.label),
                                               __firstq):
                        exit(ERROR_CODES.IMAGE_FIRSTQ_FAILED)
                # image-secondq
                elif args.image_secondq is not None:
                    check_n(header, args.image_secondq)
                    __secondq = lambda x, y: image.file_percentile(x, y, 50)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_secondq, 
                                               relabel(
                                                   "image second quartile",
                                                   args.label),
                                               __secondq):
                        exit(ERROR_CODES.IMAGE_SECONDQ_FAILED)
                # image-thirdq
                elif args.image_thirdq is not None:
                    check_n(header, args.image_thirdq)
                    __thirdq = lambda x, y: image.file_percentile(x, y, 75)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_thirdq, 
                                               relabel(
                                                   "image third quartile",
                                                   args.label),
                                               __thirdq):
                        exit(ERROR_CODES.IMAGE_THIRDQ_FAILED)
                # image-90th
                elif args.image_90th is not None:
                    check_n(header, args.image_90th)
                    __90th = lambda x, y: image.file_percentile(x, y, 90)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_90th, 
                                               relabel(
                                                   "image 90th percentile",
                                                   args.label),
                                               __90th):
                        exit(ERROR_CODES.IMAGE_90TH_FAILED)
                # image-95th
                elif args.image_95th is not None:
                    check_n(header, args.image_95th)
                    __95th = lambda x, y: image.file_percentile(x, y, 95)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_95th, 
                                               relabel(
                                                   "image 95th percentile",
                                                   args.label),
                                               __95th):
                        exit(ERROR_CODES.IMAGE_95TH_FAILED)
                # image-99th
                elif args.image_99th is not None:
                    check_n(header, args.image_99th)
                    __99th = lambda x, y: image.file_percentile(x, y, 99)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_99th, 
                                               relabel(
                                                   "image 99th percentile",
                                                   args.label),
                                               __99th):
                        exit(ERROR_CODES.IMAGE_99TH_FAILED)
                # image-joint
                elif args.image_joint is not None:
                    check_n(header, args.image_joint)
                    if d_image.file_add_column(args.dietrich, 
                                               args.image_joint, 
                                               relabel(
                                                   "image joint entropy",
                                                   args.label),
                                               image.file_joint_entropy,
                                               n_components=0):
                        exit(ERROR_CODES.IMAGE_JOINT_FAILED)
        
    # print help
    if no_command and not checked_db:
        log.warning("No command specified. Showing help.")
        parser.print_help()

if __name__ == "__main__":
    main()
