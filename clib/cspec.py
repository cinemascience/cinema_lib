
#
# Cinema spec base object
#
class CinemaSpec(object):
    CINEMA_INVALID_DATABASE = "invalid"

    def __init__(self):
        self.dbspec    = "None"
        self.dbversion = "None"

    def __del__(self):
        print("Deleting ...")

    def get_version(self):
        return self.dbversion

    def get_spec(self):
        return self.dbspec

    def check_database(self, dbname ):
        return False

