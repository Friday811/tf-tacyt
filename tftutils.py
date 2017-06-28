from __future__ import print_function
from tacyt import TacytApp


class TFTUtils(object):
    """
    Utilities for the TensorFlow-Tacyt system.

    Attributes:
        VERBOSITY: verbosity level (0-3), default 0
                   set to max verbosity if verbosity entered
                   outside 0-3 range
    """

    # Define verbosity levels:
    SILENT = -1
    ERROR = 1
    WARNING = 2
    DEBUG = 3
    levels = ['SILENT', 'ERROR', 'WARNING', 'DEBUG']

    def __init__(self, verbosity=SILENT):
        if verbosity <= self.DEBUG and verbosity >= self.SILENT:
            self.VERBOSITY = verbosity
        else:
            self.VERBOSITY = self.DEBUG
        print("Verbosity level set to: ", self.VERBOSITY)

    def vPrint(self, message, verbosity=0):
        if verbosity <= self.VERBOSITY:
            print(self.levels[verbosity] + ": " + str(message))

    @staticmethod
    def readAPI(apifile='keys.api'):
        keys = open(apifile)
        API_ID = keys.readline().rstrip('\n')[7:]
        SECRET = keys.readline().rstrip('\n')[7:]
        keys.close()
        api = TacytApp.TacytApp(API_ID, SECRET)
        return api

    @staticmethod
    def getCategoriesFromFile(fileName='APPDATA'):
        categories = []
        with open(fileName) as f:
            lines = f.readlines()
        for line in lines:
            if line[0] != '#':
                categories.append(line.rstrip('\n'))
        return categories
