"""
Command line utility for Cinema clib. Execute with "python -m clib.cl"
"""

def main():
    from . import spec
    from .spec import a
    from .spec import d
    from . import version

    import argparse
    import configparser
    import logging as log
    import textwrap
    import os

    CL_VERSION = version()

    conf_parser = argparse.ArgumentParser(
        # Turn off help, so we print all options in response to -h
        add_help=False
        )

    args, remaining_argv = conf_parser.parse_known_args()

    # Don't surpress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # Inherit options from config_parser
        parents=[conf_parser],
        # print script description with -h/--help
        epilog=textwrap.dedent('''\
            examples:
                ''')
        )

    # parser.set_defaults(**defaults)
    parser.add_argument("-a", "--astaire", 
        help="validate a Spec A database")
    parser.add_argument("-d", "--dietrich", 
        help="validate a Spec D database")
    parser.add_argument("--a2d", "--astairetodietrich",
        help="create a Spec D database from a Spec A database, in place")
    parser.add_argument("--d2s", "--dietrichtosqlite",
        help="create a SQLite3 database from a Spec D database, to ./<database_name>.db")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
        help="report verbosely")
    parser.add_argument("-q", "--quick", action="store_true", default=False,
        help="perform quick validation checks, if validating")
    parser.add_argument("--version", action="version", version=str(CL_VERSION))

    args = parser.parse_args(remaining_argv)

    # set up the proper reporting mode
    # log.info, log.warning, log.error
    if (args.verbose):
        log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', 
                        level=log.INFO, datefmt='%I:%M:%S')
    else:
        log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', 
                        level=log.WARNING, datefmt='%I:%M:%S')

    # check astaire 
    if args.astaire is not None:
        if not a.check_database(args.astaire, quick=args.quick):
            exit(True)

    # check dietrich
    elif args.dietrich is not None:
        if not d.check_database(args.dietrich, quick=args.quick):
            exit(True)

    # convert A to D
    elif args.a2d is not None:
        if not spec.convert_a_to_d(args.a2d):
            exit(True)

    elif args.d2s is not None:
        if d.get_sqlite3(args.d2s, where=os.path.splitext(
              os.path.basename(os.path.dirname(args.d2s)))[0] + ".db") == None:
            exit(True)

    # print help
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
